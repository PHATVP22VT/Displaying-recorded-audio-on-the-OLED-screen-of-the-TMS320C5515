"""
Tao template MFCC mau cho cac keyword.
Chay script nay 1 lan de sinh ra templates.npz
"""
import numpy as np
from scipy.fft import dct
from scipy.io import wavfile
import os

SAMPLE_RATE = 48000
N_MFCC      = 13
N_FFT       = 512
HOP_LENGTH  = 256
N_MELS      = 26
FMIN        = 300.0
FMAX        = 8000.0

OUTPUT_DIR  = r"E:\KTVT"

# ----------------------------------------------------------------
# MFCC pipeline (giong host_processor.py)
# ----------------------------------------------------------------
def hz_to_mel(hz):
    return 2595.0 * np.log10(1.0 + hz / 700.0)

def mel_to_hz(mel):
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

def mel_filterbank(sr, n_fft, n_mels, fmin, fmax):
    mel_min    = hz_to_mel(fmin)
    mel_max    = hz_to_mel(fmax)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points  = mel_to_hz(mel_points)
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)
    fb = np.zeros((n_mels, n_fft // 2 + 1))
    for m in range(1, n_mels + 1):
        l, c, r = bin_points[m-1], bin_points[m], bin_points[m+1]
        for k in range(l, c):
            if c != l: fb[m-1, k] = (k - l) / (c - l)
        for k in range(c, r):
            if r != c: fb[m-1, k] = (r - k) / (r - c)
    return fb

FILTERBANK = mel_filterbank(SAMPLE_RATE, N_FFT, N_MELS, FMIN, FMAX)

def compute_mfcc(audio_int16):
    audio = audio_int16.astype(np.float32) / 32768.0
    audio = np.append(audio[0], audio[1:] - 0.97 * audio[:-1])
    frames = []
    for start in range(0, len(audio) - N_FFT, HOP_LENGTH):
        frame    = audio[start:start + N_FFT] * np.hamming(N_FFT)
        spectrum = np.abs(np.fft.rfft(frame, N_FFT)) ** 2
        mel_e    = np.dot(FILTERBANK, spectrum)
        mel_e    = np.where(mel_e > 0, mel_e, 1e-10)
        mfcc     = dct(np.log(mel_e), type=2, n=N_MFCC, norm='ortho')
        frames.append(mfcc)
    if len(frames) == 0:
        return np.zeros(N_MFCC)
    return np.mean(frames, axis=0)

# ----------------------------------------------------------------
# Sinh am thanh tong hop cho tung keyword
# Moi keyword co tan so formant dac trung rieng biet
# (day la approximation - nen dung ghi am thuc te neu co the)
# ----------------------------------------------------------------
def synth_keyword(duration, formants, sr=SAMPLE_RATE):
    """Tong hop am thanh tu cac formant tan so"""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    audio = np.zeros_like(t)
    for f, amp in formants:
        audio += amp * np.sin(2 * np.pi * f * t)
    # Envelope: attack + sustain + decay
    n = len(audio)
    env = np.ones(n)
    a = int(0.05 * n)
    d = int(0.85 * n)
    env[:a]  = np.linspace(0, 1, a)
    env[d:]  = np.linspace(1, 0, n - d)
    audio *= env
    # Chuyen sang Int16
    audio /= (np.max(np.abs(audio)) + 1e-9)
    audio *= 28000
    return audio.astype(np.int16)

# Formant approximation cho moi keyword
# (f1, amp), (f2, amp), (f3, amp) - vocal tract resonances
KEYWORD_FORMANTS = {
    "XIN CHAO":    [(250, 0.9), (2200, 0.5), (3100, 0.3), (800, 0.4)],
    "HELLO":       [(300, 0.9), (1800, 0.6), (2800, 0.2), (600, 0.5)],
    "TEMPERATURE": [(200, 0.7), (1500, 0.8), (2500, 0.4), (400, 0.3)],
    "ERROR":       [(400, 0.9), (1200, 0.5), (2600, 0.3), (700, 0.6)],
    "READY":       [(350, 0.8), (2000, 0.6), (2900, 0.3), (500, 0.4)],
    "COMPLETE":    [(280, 0.7), (1700, 0.7), (2700, 0.3), (900, 0.5)],
}

DURATIONS = {
    "XIN CHAO":    1.0,
    "HELLO":       0.6,
    "TEMPERATURE": 1.4,
    "ERROR":       0.6,
    "READY":       0.7,
    "COMPLETE":    1.0,
}

# ----------------------------------------------------------------
# Tao template: moi keyword tong hop 5 bien the, lay trung binh
# ----------------------------------------------------------------
def make_template(kw):
    formants = KEYWORD_FORMANTS[kw]
    dur      = DURATIONS[kw]
    mfccs    = []
    for variation in range(5):
        # Them nhieu nho de tao bien the khac nhau
        noise_level = 0.03 + variation * 0.01
        audio = synth_keyword(dur, formants)
        noise = (np.random.randn(len(audio)) * noise_level * 28000).astype(np.int16)
        audio = np.clip(audio.astype(np.int32) + noise.astype(np.int32),
                        -32768, 32767).astype(np.int16)
        mfccs.append(compute_mfcc(audio))
    return np.mean(mfccs, axis=0)

# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "templates.npz")

    print("Dang tao template MFCC mau...\n")
    save_dict = {}
    for kw in KEYWORD_FORMANTS:
        vec = make_template(kw)
        save_dict[kw.replace(" ", "_")] = vec
        print(f"  [{kw}]: MFCC = {np.round(vec[:4], 2)}...")

    np.savez(out_path, **save_dict)
    print(f"\nDa luu templates.npz vao {out_path}")
    print("Chay host_processor.py la dung duoc ngay.")
    print("\nLUU Y: Template nay duoc tong hop, khong phai ghi am thuc te.")
    print("De chinh xac hon, chay host_processor.py -> nhan T -> ghi am that.")
