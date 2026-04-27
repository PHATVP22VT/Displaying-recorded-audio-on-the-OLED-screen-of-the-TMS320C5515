"""
Test UART thu cong - go text tren ban phim, gui xuong ATmega328P
Dung de test mach Proteus TRUOC khi dung mic that

Fix: Gui ca \r\n de Proteus COMPIM khong nuot mat ky tu ket thuc
Chay: python test_uart.py
"""

import serial
import time
import sys

SERIAL_PORT = "COM2"
BAUD_RATE   = 9600

def main():
    print("=" * 45)
    print("  Test UART thu cong  |  Go text -> OLED")
    print("=" * 45)

    try:
        ser = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1,
            # Quan trong: Proteus COMPIM can RTS/CTS tat
            rtscts=False,
            dsrdtr=False
        )
        print(f"[OK] Ket noi {SERIAL_PORT} @ {BAUD_RATE} baud\n")
    except serial.SerialException as e:
        print(f"[LOI] {e}")
        sys.exit(1)

    print("Go text roi Enter de gui len OLED.")
    print("Go 'quit' de thoat.\n")

    while True:
        try:
            text = input(">> ").strip()
            if text.lower() == "quit":
                break
            if not text:
                continue

            # Cat 20 ky tu, gui kem \r\n (CRLF) - Proteus COMPIM xu ly tot hon
            payload = (text[:20] + "\r\n").encode("ascii", errors="ignore")
            ser.write(payload)
            # Flush ngay lap tuc
            ser.flush()
            print(f"[UART] Da gui: '{text[:20]}' ({len(payload)} bytes)")

        except KeyboardInterrupt:
            break

    ser.close()
    print("\n[OK] Da dong cong COM.")

if __name__ == "__main__":
    main()