#include "ezdsp5535.h"
#include "ezdsp5535_lcd.h"
#include "oled_display.h"
#include "oled_font.h"
#include <string.h>

static void print_char(Uint16 c1, Uint16 c2, Uint16 c3, Uint16 c4)
{
    EZDSP5535_OSD9616_printLetter(c1, c2, c3, c4);
    EZDSP5535_OSD9616_send(0x40, 0x00); /* 1 cot khoang cach (space) sau moi chu */
}

static void print_spaces(Int16 n)
{
    Int16 i;
    for (i = 0; i < n; i++)
        EZDSP5535_OSD9616_send(0x40, 0x00);
}

static void set_page(Int16 p)
{
    EZDSP5535_OSD9616_send(0x00, 0x00);        
    EZDSP5535_OSD9616_send(0x00, 0x10);        
    EZDSP5535_OSD9616_send(0x00, 0xb0 + p);    
}

void OLED_init(void)
{
    EZDSP5535_OSD9616_init();
    EZDSP5535_OSD9616_send(0x00, 0x2e); /* Tat tinh nang cuon */
    OLED_clear();
}

void OLED_clear(void)
{
    Int16 i;
    set_page(0);
    for (i = 0; i < 128; i++) EZDSP5535_OSD9616_send(0x40, 0x00);
    set_page(1);
    for (i = 0; i < 128; i++) EZDSP5535_OSD9616_send(0x40, 0x00);
}

/* Ham ve 1 ky tu tu Font A-Z hoac Space */
/* Ham ve 1 ky tu tu Font A-Z hoac Space */
static void draw_letter(char c)
{
    if (c >= 'A' && c <= 'Z') {
        Int16 idx = c - 'A';
        /* DAO NGUOC THU TU TRUYEN: 3 -> 2 -> 1 -> 0 de lat chu lai dung chieu */
        print_char(FONT_A_Z[idx][3], FONT_A_Z[idx][2], FONT_A_Z[idx][1], FONT_A_Z[idx][0]);
    } else {
        /* Khoang trang (Space) hoac ky tu la */
        print_char(0x00, 0x00, 0x00, 0x00); 
    }
}

/* =========================================================
 * Ham in chuoi dong, ho tro toi da 50 ky tu (2 dong)
 * IN NGUOC de khac phuc loi hien thi phai-sang-trai
 * ========================================================= */
void OLED_printString(char *text)
{
    Int16 len = strlen(text);
    Int16 p0_len = (len > 25) ? 25 : len;          /* So ky tu dong 1 */
    Int16 p1_len = (len > 25) ? (len - 25) : 0;    /* So ky tu dong 2 */
    Int16 i;
    
    if (p1_len > 25) p1_len = 25; /* Gioi han tong max 50 */

    OLED_clear();
    EZDSP5535_OSD9616_send(0x00, 0x2e); 

    /* --- Xu ly Page 0 (Dong 1) --- */
    set_page(0);
    print_spaces((128 - p0_len * 5) / 2); /* Can giua */
    
    /* In nguoc tu cuoi dong 1 ve dau dong 1 */
    for (i = p0_len - 1; i >= 0; i--)
    {
        draw_letter(text[i]);
    }

    /* --- Xu ly Page 1 (Dong 2) --- */
    if (p1_len > 0)
    {
        set_page(1);
        print_spaces((128 - p1_len * 5) / 2); /* Can giua */
        
        /* In nguoc tu cuoi dong 2 ve dau dong 2 */
        for (i = p0_len + p1_len - 1; i >= p0_len; i--)
        {
            draw_letter(text[i]);
        }
    }
}