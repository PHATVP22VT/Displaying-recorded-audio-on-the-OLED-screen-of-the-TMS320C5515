/*
 * ssd1306.h — Driver OLED SSD1306 128x64 qua I2C (TWI)
 * Target: ATmega328P @ 16 MHz
 *
 * API công khai:
 *   ssd1306_init()              — Kh?i t?o màn hình
 *   ssd1306_clear()             — Xoá toàn b? màn hình
 *   ssd1306_set_cursor(col, row) — ??t v? trí con tr? (col: 0-20, row: 0-7)
 *   ssd1306_print_char(c)       — In 1 ký t? ASCII
 *   ssd1306_print_str(s)        — In chu?i ASCII
 */

#ifndef SSD1306_H
#define SSD1306_H

#include <stdint.h>

/* ??a ch? I2C c?a SSD1306 (0x3C ho?c 0x3D tu? chân SA0) */
#define SSD1306_I2C_ADDR   0x3C

/* Kích th??c màn hình */
#define SSD1306_WIDTH   128
#define SSD1306_HEIGHT   64

void ssd1306_init(void);
void ssd1306_clear(void);
void ssd1306_set_cursor(uint8_t col, uint8_t row);
void ssd1306_print_char(char c);
void ssd1306_print_str(const char *s);

#endif /* SSD1306_H */