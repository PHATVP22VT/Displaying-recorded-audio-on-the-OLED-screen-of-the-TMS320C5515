"""
Speech-to-OLED: Thu am thanh tu mic, nhan dang giong noi, gui text qua UART
Ket noi: PC (Python) --> COM ao --> Proteus (ATmega328P) --> OLED SSD1306

Yeu cau cai dat:
    pip install SpeechRecognition pyaudio pyserial

    Neu loi pyaudio tren Windows:
    pip install pipwin
    pipwin install pyaudio
"""

import speech_recognition as sr
import serial
import time
import sys

# ============================================================
# CAU HINH
# ============================================================
SERIAL_PORT = "COM2"
BAUD_RATE   = 9600
LANGUAGE    = "en-US"

# ============================================================
# 5 TEST CASE - kiem tra chuc nang hien thi OLED
# ============================================================
TEST_CASES = [
    {
        "phrase": "Hi",
        "desc":   "TC1 - Short string (2 chars): verify screen clears old content"
    },
    {
        "phrase": "Test 123 OK",
        "desc":   "TC2 - Mixed letters & digits: verify font renders both correctly"
    },
    {
        "phrase": "Hello! #AVR @3.3V",
        "desc":   "TC3 - Special chars (! # @ .): verify ASCII special symbols display"
    },
    {
        "phrase": "ABCDEFGHIJKLMNOPQRST",
        "desc":   "TC4 - Max length 20 chars: verify no overflow or missing last char"
    },
    {
        "phrase": "Screen updated!!!!!",
        "desc":   "TC5 - Rapid update after TC4: verify full redraw replaces old text"
    },
]

# ============================================================

RESET    = "\033[0m"
BOLD     = "\033[1m"
CYAN     = "\033[96m"
GREEN    = "\033[92m"
YELLOW   = "\033[93m"
RED      = "\033[91m"
MAGENTA  = "\033[95m"

def connect_serial(port, baud):
    while True:
        try:
            ser = serial.Serial(port, baud, timeout=1, rtscts=False, dsrdtr=False)
            print(f"{GREEN}[OK] Connected to {port} @ {baud} baud{RESET}")
            return ser
        except serial.SerialException as e:
            print(f"{RED}[ERR] Cannot open {port}: {e}{RESET}")
            print("      Check com0com pair. Retrying in 3s...")
            time.sleep(3)


def send_text(ser, text):
    """
    Gui chuoi text qua UART.
    Format: <text>\r\n
    Gioi han 20 ky tu cho OLED 128x64 font 6x8
    """
    text = text.strip()[:20]
    encoded = text.encode("ascii", errors="ignore").decode("ascii")
    if not encoded:
        encoded = "???"
    payload = encoded + "\r\n"
    ser.write(payload.encode("ascii"))
    ser.flush()
    print(f"{GREEN}[UART] Sent: '{encoded}'{RESET}")


def print_banner():
    print(f"\n{CYAN}{'='*50}{RESET}")
    print(f"{BOLD}{CYAN}   Speech-to-OLED  |  ATmega328P + SSD1306{RESET}")
    print(f"{CYAN}{'='*50}{RESET}\n")


def print_menu():
    print(f"\n{BOLD}Select mode:{RESET}")
    print(f"  {YELLOW}[1]{RESET} Microphone mode  - Speak into mic")
    print(f"  {YELLOW}[2]{RESET} Test case mode   - Send preset phrases")
    print(f"  {YELLOW}[q]{RESET} Quit")
    print(f"\n{BOLD}>> {RESET}", end="", flush=True)


def mode_microphone(ser):
    """Mode 1: Nhan dang giong noi qua mic va gui UART."""
    print(f"\n{CYAN}--- Microphone Mode ---{RESET}")
    print(f"Press {YELLOW}Ctrl+C{RESET} to return to menu.\n")

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    mic = sr.Microphone()

    print(f"{YELLOW}[INFO] Calibrating ambient noise (2s, stay quiet)...{RESET}")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
    print(f"{GREEN}[OK] Ready! Speak into the mic.{RESET}")
    print(f"     Press Ctrl+C to go back to menu.\n")

    while True:
        try:
            with mic as source:
                print(f"{MAGENTA}[MIC] Listening...{RESET}")
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                except sr.WaitTimeoutError:
                    print(f"{YELLOW}[INFO] No audio detected, retrying...{RESET}")
                    continue

            print(f"{YELLOW}[STT] Recognizing...{RESET}")
            try:
                text = recognizer.recognize_google(audio, language=LANGUAGE)
                print(f"{GREEN}[STT] Recognized: '{text}'{RESET}")
                send_text(ser, text)
            except sr.UnknownValueError:
                print(f"{RED}[STT] Could not understand audio{RESET}")
            except sr.RequestError as e:
                print(f"{RED}[ERR] Google API error: {e}{RESET}")
                print("      Check internet connection.")

        except KeyboardInterrupt:
            print(f"\n{YELLOW}[INFO] Returning to menu...{RESET}")
            return


def mode_test_cases(ser):
    """Mode 2: Gui tung doan text test case, cho xac nhan truoc moi doan."""
    print(f"\n{CYAN}--- Test Case Mode ---{RESET}")
    print(f"Press Enter to send each phrase. Press {YELLOW}Ctrl+C{RESET} to return to menu.\n")

    print(f"{BOLD}Test cases:{RESET}")
    for i, tc in enumerate(TEST_CASES, 1):
        print(f"  {YELLOW}[{i}]{RESET} \"{tc['phrase']}\"")
        print(f"       {tc['desc']}")
    print()

    try:
        for i, tc in enumerate(TEST_CASES, 1):
            phrase = tc["phrase"]
            print(f"{BOLD}--- Test {i}/{len(TEST_CASES)} ---{RESET}")
            print(f"  Phrase  : {CYAN}\"{phrase}\"{RESET}")
            print(f"  Length  : {len(phrase)} chars")
            print(f"  Purpose : {tc['desc']}")
            input(f"  {YELLOW}Press Enter to send...{RESET} ")

            send_text(ser, phrase)
            print(f"{GREEN}  [OK] Sent! Check OLED display.{RESET}\n")

            # Doi nguoi dung kiem tra OLED xong roi moi tiep
            if i < len(TEST_CASES):
                input(f"  {YELLOW}Press Enter to continue to next test...{RESET} ")
                print()

        print(f"\n{GREEN}[DONE] All {len(TEST_CASES)} test cases sent!{RESET}")
        input(f"\n{YELLOW}Press Enter to return to menu...{RESET} ")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}[INFO] Returning to menu...{RESET}")
        return


def main():
    print_banner()

    ser = connect_serial(SERIAL_PORT, BAUD_RATE)

    while True:
        print_menu()
        try:
            choice = input().strip().lower()
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}[INFO] Exiting...{RESET}")
            ser.close()
            print(f"{GREEN}[OK] COM port closed. Goodbye!{RESET}")
            sys.exit(0)

        if choice == "1":
            mode_microphone(ser)
        elif choice == "2":
            mode_test_cases(ser)
        elif choice == "q":
            break
        else:
            print(f"{RED}[ERR] Invalid choice. Enter 1, 2 or q.{RESET}")

    ser.close()
    print(f"\n{GREEN}[OK] COM port closed. Goodbye!{RESET}")


if __name__ == "__main__":
    main()