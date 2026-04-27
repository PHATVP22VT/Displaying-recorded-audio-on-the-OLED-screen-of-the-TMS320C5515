/*
 * Speech-to-OLED Firmware  [FIX v2]
 * Target  : ATmega328P @ 16 MHz
 * Toolchain: Microchip Studio (AVR-GCC)
 *
 * Fix v2:
 *   - Tang IDLE_TIMEOUT_MS len 300ms (tranh flush qua som)
 *   - ISR chap nhan ca '\r', '\n', "\r\n"
 *   - Bo cli/sei bao quanh strncpy (khong can thiet o day)
 */

#define F_CPU 8000000UL

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <string.h>
#include "ssd1306.h"

/* ================================================================
   UART - 9600 baud @ 16 MHz
   ================================================================ */
#define BAUD        9600
#define UBRR_VAL    (F_CPU / 16 / BAUD - 1)

#define UART_BUF_SIZE  32

static volatile char    uart_buf[UART_BUF_SIZE];
static volatile uint8_t uart_idx   = 0;
static volatile uint8_t uart_ready = 0;
static volatile uint8_t has_data   = 0;
static volatile uint16_t idle_ticks = 0;
static volatile uint8_t led_count  = 0;

/* ================================================================
   TIMER0 - CTC ~1ms, dem idle sau ky tu cuoi
   Neu qua IDLE_TIMEOUT_MS ma chua co '\n' -> tu dong flush
   ================================================================ */
#define IDLE_TIMEOUT_MS  300   /* Tang len 300ms cho Proteus COMPIM */

static void timer0_init(void)
{
    TCCR0A = (1 << WGM01);               /* CTC mode */
    TCCR0B = (1 << CS01) | (1 << CS00);  /* Prescaler 64 */
    OCR0A  = 249;                         /* 16M/64/1000 - 1 = 249 -> ~1ms */
    TIMSK0 = (1 << OCIE0A);
}

ISR(TIMER0_COMPA_vect)
{
    if (has_data && !uart_ready) {
        idle_ticks++;
        if (idle_ticks >= IDLE_TIMEOUT_MS) {
            uart_buf[uart_idx] = '\0';
            uart_ready  = 1;
            idle_ticks  = 0;
            has_data    = 0;
        }
    }
}

/* ================================================================
   UART init + ISR
   ================================================================ */
void uart_init(void)
{
    UBRR0H = (uint8_t)(UBRR_VAL >> 8);
    UBRR0L = (uint8_t)(UBRR_VAL);
    UCSR0B = (1 << RXEN0) | (1 << TXEN0) | (1 << RXCIE0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

ISR(USART_RX_vect)
{
    char c = UDR0;

    if (uart_ready) return;

    if (c == '\n' || c == '\r') {
        /* Nhan duoc ky tu ket thuc */
        if (uart_idx > 0) {
            uart_buf[uart_idx] = '\0';
            uart_ready  = 1;
            idle_ticks  = 0;
            has_data    = 0;
        }
        /* Neu uart_idx == 0: bo qua '\r' thu 2 cua CRLF */
    } else {
        if (uart_idx < UART_BUF_SIZE - 1) {
            uart_buf[uart_idx++] = c;
            idle_ticks = 0;   /* Reset dem idle */
            has_data   = 1;

            /* Cap nhat Bar LED */
            led_count++;
            if (led_count > 6) led_count = 1;
            PORTB = (1 << led_count) - 1;

        } else {
            /* Buffer day -> flush ngay */
            uart_buf[uart_idx] = '\0';
            uart_ready = 1;
            idle_ticks = 0;
            has_data   = 0;
        }
    }
}

/* ================================================================
   MAIN
   ================================================================ */
int main(void)
{
    char display_buf[UART_BUF_SIZE];

    /* PORTB -> Bar LED output */
    DDRB  |= 0x3F;
    PORTB  = 0x00;

    uart_init();
    timer0_init();
    ssd1306_init();
    sei();

    /* Man hinh chao */
    ssd1306_clear();
    ssd1306_set_cursor(0, 0);
    ssd1306_print_str("Speech to OLED");
    ssd1306_set_cursor(0, 2);
    ssd1306_print_str("Waiting...");

    while (1) {
        if (uart_ready) {
            /* Sao chep buffer (ngan ngat trong luc copy) */
            cli();
            strncpy(display_buf, (const char *)uart_buf, UART_BUF_SIZE);
            uart_idx   = 0;
            uart_ready = 0;
            has_data   = 0;
            idle_ticks = 0;
            sei();

            /* Tat LED, don cho cau moi */
            led_count = 0;
            PORTB     = 0x00;

            /* Hien thi OLED */
            ssd1306_clear();
            ssd1306_set_cursor(0, 0);
            ssd1306_print_str("Heard:");
            ssd1306_set_cursor(0, 2);
            ssd1306_print_str(display_buf);
        }
    }
}