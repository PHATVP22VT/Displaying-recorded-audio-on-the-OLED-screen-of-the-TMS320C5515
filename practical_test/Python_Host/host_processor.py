"""
HOST PROCESSOR - PHIÊN BẢN HOÀN THIỆN
========================================
Luồng xử lý:
  Giai đoạn 1 : Nhấn Enter -> VAD -> Thu âm động
  Giai đoạn 2 : MFCC (Hamming + Mel + DCT + CMS)
  Giai đoạn 3 : FastDTW so khớp template
  Giai đoạn 4 : Giao tiếp DSP qua cmd.txt -> OLED

Tính năng bổ sung:
  [A] Thêm template từ mới
  [D] Xóa template
  [L] Xem danh sách template
  [R] Nhận dạng (luồng chính)
  [Q] Thoát
"""

import sounddevice as sd
import numpy as np
import time
import os
import sys
from scipy.fft import dct
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

# ================================================================
# CẤU HÌNH HỆ THỐNG
# ================================================================
BASE_DIR             = r"E:\KTVT"
CMD_FILE             = os.path.join(BASE_DIR, "cmd.txt")
TEMPLATE_FILE        = os.path.join(BASE_DIR, "templates.npz")

# Thông số âm thanh - đồng bộ với MATLAB
SAMPLE_RATE          = 16000
FRAME_SIZE           = 256       # 16 ms mỗi khung
HOP_SIZE             = 128       # Bước nhảy 8 ms (overlap 50%)
N_MFCC               = 13
N_FILTERS            = 26
F_LOW                = 300       # Hz
F_HIGH               = 8000      # Hz

# VAD
ENERGY_THRESH        = 800       # Ngưỡng phát hiện giọng nói
SILENCE_THRESH       = 10        # Số frame im lặng liên tiếp để kết thúc
MAX_FRAMES           = 250       # Giới hạn tối đa (~4 giây)
MIN_FRAMES           = 15        # Tối thiểu để tránh nhiễu

# DTW
DTW_ACCEPT_THRESH    = 100.0     # Score DTW tối đa để chấp nhận kết quả
N_TEMPLATES_PER_KW   = 5         # Số mẫu tối đa lưu mỗi từ khóa

# Từ khóa mặc định (có thể thêm bất kỳ từ mới nào qua menu)
DEFAULT_KEYWORDS     = ["XIN CHAO", "HELLO", "TEMP", "ERROR", "READY", "COMPLETE"]

# ================================================================
# KHỞI TẠO MEL FILTERBANK (tính 1 lần khi load)
# ================================================================
def _build_filterbank() -> np.ndarray:
    mel_low  = 2595.0 * np.log10(1.0 + F_LOW  / 700.0)
    mel_high = 2595.0 * np.log10(1.0 + F_HIGH / 700.0)
    mel_pts  = np.linspace(mel_low, mel_high, N_FILTERS + 2)
    hz_pts   = 700.0 * (10.0 ** (mel_pts / 2595.0) - 1.0)
    bins     = np.floor((FRAME_SIZE + 1) * hz_pts / SAMPLE_RATE).astype(int)

    n_half   = FRAME_SIZE // 2 + 1
    fbank    = np.zeros((N_FILTERS, n_half))
    for j in range(N_FILTERS):
        for i in range(bins[j],   bins[j + 1]):
            fbank[j, i] = (i - bins[j])       / (bins[j + 1] - bins[j])
        for i in range(bins[j+1], bins[j + 2]):
            fbank[j, i] = (bins[j + 2] - i)   / (bins[j + 2] - bins[j + 1])
    return fbank

FILTERBANK = _build_filterbank()

# ================================================================
# MODULE MFCC
# ================================================================
def compute_mfcc(audio_int16: np.ndarray) -> np.ndarray:
    """
    Tính ma trận MFCC từ mảng Int16.
    Trả về ma trận shape (n_frames, N_MFCC) sau CMS.
    """
    audio  = audio_int16.astype(np.float32) / 32768.0
    window = np.hamming(FRAME_SIZE)
    frames = []

    for start in range(0, len(audio) - FRAME_SIZE + 1, HOP_SIZE):
        frame    = audio[start : start + FRAME_SIZE] * window
        mag_spec = np.abs(np.fft.rfft(frame, FRAME_SIZE))        # rfft = chỉ nửa dương
        fout     = FILTERBANK @ mag_spec                          # 26 giá trị Mel
        log_fout = np.log(np.maximum(fout, 1e-10))               # tránh log(0)
        mfcc     = dct(log_fout, type=2, norm='ortho')[:N_MFCC]
        frames.append(mfcc)

    if not frames:
        return np.zeros((1, N_MFCC), dtype=np.float32)

    mat = np.array(frames, dtype=np.float32)
    mat -= mat.mean(axis=0)   # CMS: loại bỏ tạp âm kênh truyền
    return mat

# ================================================================
# MODULE TEMPLATE DATABASE
# ================================================================
class TemplateDB:
    """
    Quản lý cơ sở dữ liệu template.
    Mỗi từ khóa lưu tối đa N_TEMPLATES_PER_KW mẫu MFCC.
    File lưu: .npz với key = "<KEYWORD>_<idx>" (vd: HELLO_0, HELLO_1)
    """

    def __init__(self, path: str):
        self.path      = path
        self.db: dict  = {}   # { "HELLO": [mfcc_mat, mfcc_mat, ...], ... }
        self._load()

    # ---- Persistence ------------------------------------------------

    def _load(self):
        self.db = {}
        if not os.path.exists(self.path):
            print("[DB] Chưa có file template. Dùng [A] để thu âm mẫu mới.")
            return
        try:
            data = np.load(self.path, allow_pickle=True)
            for raw_key in data.files:
                # raw_key = "HELLO_0", "XIN CHAO_2", ...
                parts = raw_key.rsplit("_", 1)
                if len(parts) != 2:
                    continue
                kw = parts[0]
                if kw not in self.db:
                    self.db[kw] = []
                self.db[kw].append(data[raw_key])
            total = sum(len(v) for v in self.db.values())
            print(f"[DB] Đã tải {total} mẫu cho {len(self.db)} từ khóa.")
        except Exception as e:
            print(f"[DB][LỖI] Không đọc được file template: {e}")

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        save_dict = {}
        for kw, mats in self.db.items():
            for idx, mat in enumerate(mats):
                save_dict[f"{kw}_{idx}"] = mat
        np.savez(self.path, **save_dict)
        print(f"[DB] Đã lưu {len(save_dict)} mẫu vào {self.path}")

    # ---- CRUD -------------------------------------------------------

    def add(self, keyword: str, mfcc_mat: np.ndarray):
        kw = keyword.strip().upper()
        if kw not in self.db:
            self.db[kw] = []
        if len(self.db[kw]) >= N_TEMPLATES_PER_KW:
            # Xóa mẫu cũ nhất (FIFO)
            self.db[kw].pop(0)
            print(f"[DB] Đã đủ {N_TEMPLATES_PER_KW} mẫu, xóa mẫu cũ nhất của '{kw}'.")
        self.db[kw].append(mfcc_mat)
        print(f"[DB] Đã thêm mẫu #{len(self.db[kw])} cho '{kw}'.")
        self.save()

    def delete(self, keyword: str):
        kw = keyword.strip().upper()
        if kw in self.db:
            del self.db[kw]
            self.save()
            print(f"[DB] Đã xóa toàn bộ mẫu của '{kw}'.")
        else:
            print(f"[DB] Không tìm thấy từ khóa '{kw}'.")

    def list_keywords(self):
        if not self.db:
            print("[DB] Cơ sở dữ liệu đang trống.")
            return
        print("\n┌─ DANH SÁCH TEMPLATE ─────────────────────────")
        for kw, mats in sorted(self.db.items()):
            shapes = [m.shape for m in mats]
            print(f"│  {kw:<20} : {len(mats)} mẫu  {shapes}")
        print("└───────────────────────────────────────────────")

    def has_any(self) -> bool:
        return any(len(v) > 0 for v in self.db.values())

# ================================================================
# MODULE VAD + THU ÂM
# ================================================================
def _record_one_utterance() -> np.ndarray | None:
    """
    Nghe mic theo VAD:
      - Chờ phát hiện giọng (energy > ENERGY_THRESH)
      - Ghi cho đến khi im lặng kéo dài hoặc MAX_FRAMES
    Trả về mảng Int16, hoặc None nếu quá ngắn/lỗi.
    """
    buf = []

    def _cb(indata, frames, time_info, status):
        buf.append((indata[:, 0] * 32767).astype(np.int16).copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        blocksize=FRAME_SIZE, callback=_cb):
        # Xóa rác buffer tích lũy trong lúc chờ nhấn phím
        time.sleep(0.1)
        buf.clear()

        state         = "IDLE"
        frame_accum   = []
        silence_count = 0

        print(">>> [MIC] Đang nghe... Hãy nói từ khóa.")

        while True:
            if not buf:
                time.sleep(0.005)
                continue

            frame  = buf.pop(0)
            energy = int(np.sum(np.abs(frame)))

            if state == "IDLE":
                if energy > ENERGY_THRESH:
                    state         = "REC"
                    frame_accum   = [frame]
                    silence_count = 0
                    print(f"[MIC] Phát hiện giọng (energy={energy}). Đang ghi...")

            elif state == "REC":
                frame_accum.append(frame)
                if energy <= ENERGY_THRESH:
                    silence_count += 1
                else:
                    silence_count = 0

                if silence_count > SILENCE_THRESH or len(frame_accum) >= MAX_FRAMES:
                    break   # kết thúc thu âm

    if len(frame_accum) < MIN_FRAMES:
        print(f"[MIC] Âm thanh quá ngắn ({len(frame_accum)} frames). Bỏ qua.")
        return None

    audio = np.concatenate(frame_accum)
    print(f"[MIC] Ghi xong: {len(frame_accum)} frames "
          f"({len(audio)/SAMPLE_RATE:.2f}s)")
    return audio

# ================================================================
# MODULE DTW NHẬN DẠNG
# ================================================================
def recognize(mfcc_mat: np.ndarray, db: TemplateDB) -> tuple[str | None, float]:
    """
    So khớp FastDTW với tất cả mẫu trong DB.
    Trả về (best_keyword, best_score) hoặc (None, score) nếu vượt ngưỡng.
    """
    best_kw   = None
    best_dist = float("inf")

    for kw, templates in db.db.items():
        kw_scores = []
        for tmpl in templates:
            dist, path = fastdtw(mfcc_mat, tmpl, dist=euclidean)
            norm_dist  = dist / max(len(path), 1)
            kw_scores.append(norm_dist)
        # Lấy điểm trung bình của tất cả mẫu cho từ khóa này
        avg_score = float(np.mean(kw_scores))
        if avg_score < best_dist:
            best_dist = avg_score
            best_kw   = kw

    accepted = best_dist < DTW_ACCEPT_THRESH
    status   = "✓ CHẤP NHẬN" if accepted else "✗ KHÔNG RÕ"
    print(f"   -> Kết quả: {best_kw}  |  Score: {best_dist:.1f}  |  {status}")
    return (best_kw if accepted else None, best_dist)

# ================================================================
# MODULE GIAO TIẾP DSP
# ================================================================
def send_to_dsp(keyword: str, timeout: float = 10.0):
    """Ghi lệnh vào cmd.txt và chờ DSP xác nhận (-1)."""
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(CMD_FILE, "w") as f:
        f.write(f"{keyword}#")
    print(f"[DSP] Đã gửi lệnh: '{keyword}' -> Chờ DSP xử lý OLED...")

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with open(CMD_FILE, "r") as f:
                content = f.read().strip()
            if content == "-1":
                print("[DSP] DSP đã hiển thị xong OLED.")
                return True
        except Exception:
            pass
        time.sleep(0.1)

    print(f"[DSP][TIMEOUT] DSP không phản hồi sau {timeout}s.")
    return False

def reset_cmd_file():
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(CMD_FILE, "w") as f:
        f.write("-1")

# ================================================================
# LUỒNG CHÍNH: NHẬN DẠNG
# ================================================================
def flow_recognize(db: TemplateDB):
    if not db.has_any():
        print("[!] Chưa có template. Dùng [A] để thêm mẫu trước.")
        return

    try:
        input("\n[ENTER] Nhấn Enter khi sẵn sàng nói...")
    except KeyboardInterrupt:
        return

    # Giai đoạn 1: Thu âm
    audio = _record_one_utterance()
    if audio is None:
        return

    # Giai đoạn 2: MFCC
    mfcc_mat = compute_mfcc(audio)
    print(f"[MFCC] Shape: {mfcc_mat.shape}")

    # Giai đoạn 3: DTW
    result, score = recognize(mfcc_mat, db)

    # Giai đoạn 4: Giao tiếp DSP
    if result:
        send_to_dsp(result)
    else:
        print("[!] Không nhận dạng được. Thử lại.")

# ================================================================
# LUỒNG PHỤ: THÊM TEMPLATE
# ================================================================
def flow_add_template(db: TemplateDB):
    print("\n── THÊM TEMPLATE MỚI ─────────────────────────────")
    kw = input("   Nhập từ khóa (VD: XIN CHAO): ").strip().upper()
    if not kw:
        print("[!] Từ khóa không được để trống.")
        return

    current_count = len(db.db.get(kw, []))
    remaining     = N_TEMPLATES_PER_KW - current_count
    print(f"   Từ khóa: '{kw}' | Hiện có: {current_count} mẫu | Tối đa: {N_TEMPLATES_PER_KW}")

    try:
        n = int(input(f"   Thu bao nhiêu mẫu? (còn chỗ {remaining}, khuyến nghị >= 3): ") or "3")
        n = max(1, min(n, N_TEMPLATES_PER_KW))
    except ValueError:
        n = 3

    for i in range(n):
        print(f"\n   --- Mẫu {i+1}/{n} ---")
        try:
            input(f"   [ENTER] Nhấn Enter rồi nói '{kw}'...")
        except KeyboardInterrupt:
            print("\n[!] Hủy thu âm.")
            return

        audio = _record_one_utterance()
        if audio is None:
            print(f"   [!] Mẫu {i+1} bị bỏ qua (quá ngắn).")
            continue

        mfcc_mat = compute_mfcc(audio)
        db.add(kw, mfcc_mat)
        print(f"   [OK] Đã lưu mẫu {i+1} cho '{kw}' | Shape: {mfcc_mat.shape}")

    print(f"\n[OK] Hoàn tất. '{kw}' hiện có {len(db.db.get(kw, []))} mẫu.")

# ================================================================
# LUỒNG PHỤ: XÓA TEMPLATE
# ================================================================
def flow_delete_template(db: TemplateDB):
    print("\n── XÓA TEMPLATE ───────────────────────────────────")
    db.list_keywords()
    if not db.has_any():
        return
    kw = input("   Nhập từ khóa muốn xóa (hoặc Enter để hủy): ").strip().upper()
    if not kw:
        return
    confirm = input(f"   Xác nhận xóa '{kw}'? (y/N): ").strip().lower()
    if confirm == "y":
        db.delete(kw)

# ================================================================
# MENU CHÍNH
# ================================================================
def print_menu():
    print("\n" + "=" * 52)
    print("   HỆ THỐNG NHẬN DẠNG TIẾNG NÓI - DSP C5515")
    print("=" * 52)
    print("  [R] Nhận dạng từ khóa (luồng chính)")
    print("  [A] Thêm template từ mới")
    print("  [D] Xóa template")
    print("  [L] Xem danh sách template")
    print("  [Q] Thoát")
    print("-" * 52)

def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    reset_cmd_file()

    db = TemplateDB(TEMPLATE_FILE)

    # Nếu DB còn trống, hỏi có muốn thêm mẫu ngay không
    if not db.has_any():
        print("\n[!] Chưa có template nào trong database.")
        ans = input("   Bạn muốn thu âm mẫu ngay bây giờ không? (y/N): ").strip().lower()
        if ans == "y":
            flow_add_template(db)

    while True:
        print_menu()
        db.list_keywords()
        choice = input("  Lựa chọn: ").strip().upper()

        if choice == "R":
            flow_recognize(db)
        elif choice == "A":
            flow_add_template(db)
        elif choice == "D":
            flow_delete_template(db)
        elif choice == "L":
            db.list_keywords()
        elif choice in ("Q", "EXIT", "QUIT"):
            print("Đã thoát chương trình.")
            sys.exit(0)
        else:
            print("[!] Lựa chọn không hợp lệ.")

if __name__ == "__main__":
    main()