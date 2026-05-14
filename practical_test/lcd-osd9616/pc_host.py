import os
import time
import speech_recognition as sr
from unidecode import unidecode

TEMP_DIR = r"E:\KTVT\setup_CCS_4.2.5.00005\setup_CCS_4.2.5.00005\ezdsp5535_BSL_RevC\ezdsp5535_v1\tests\lcd-osd9616\temp"
CMD_FILE = os.path.join(TEMP_DIR, "cmd.txt")
os.makedirs(TEMP_DIR, exist_ok=True)

recognizer = sr.Recognizer()

print("=== HE THONG NHAN DIEN GIONG NOI ===")
print("Ban co the noi tieng Viet...")

while True:
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            recognizer.dynamic_energy_threshold = True
            print("\n[Dang nghe...]")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
            
        # 1. Nhan dien bang Tieng Viet
        raw_text = recognizer.recognize_google(audio, language="vi-VN")
        
        # 2. Chuyen thanh chu IN HOA va BO DAU (VD: "Xin chào" -> "XIN CHAO")
        text = unidecode(raw_text).upper()
        
        # Gioi han 50 ky tu
        if len(text) > 50:
            text = text[:50] 

        print(f"-> Nhan dien goc: {raw_text}")
        print(f"-> Da chuyen doi: {text}")

        with open(CMD_FILE, "w") as f:
            f.write(text + "#")
            
        time.sleep(1.5)

    except sr.UnknownValueError:
        print("-> Khong nghe ro, hay noi lai!")
    except sr.WaitTimeoutError:
        pass
    except KeyboardInterrupt:
        break