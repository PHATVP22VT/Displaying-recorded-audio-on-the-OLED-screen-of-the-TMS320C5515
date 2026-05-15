#ifndef OLED_DISPLAY_H
#define OLED_DISPLAY_H

#include "ezdsp5535.h"

/* Cac ham giao tiep OLED */
void OLED_init(void);
void OLED_clear(void);
void OLED_printString(char *text); /* Ham moi nhan chuoi ky tu bat ky */

#endif /* OLED_DISPLAY_H */