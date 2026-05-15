#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ezdsp5535.h"
#include "ezdsp5535_i2c.h"
#include "oled_display.h"

#define CMD_FILE_PATH   "E:\\KTVT\\cmd.txt"

static void delay_ms(Uint32 ms) {
    volatile Uint32 i, j;
    for (i = 0; i < ms; i++) for (j = 0; j < 2000; j++);
}

void main(void)
{
    FILE *fp;
    char buffer[60];
    char c, next_c;
    int idx;

    printf("\n=== HE THONG HIEN THI OLED (PERSISTENT RECEIVER) ===\n");
    
    EZDSP5535_init();
    EZDSP5535_I2C_init();
    OLED_init();
    OLED_clear();
    OLED_printString("SAN SANG");

    fp = fopen(CMD_FILE_PATH, "w");
    if(fp) { 
        fputs("-1", fp); 
        fclose(fp); 
    }

    while(1)
    {
        fp = fopen(CMD_FILE_PATH, "r");
        
        idx = 0; // Reset idx moi vong lap
        memset(buffer, 0, sizeof(buffer));

        if(fp != NULL) {
            while((c = fgetc(fp)) != EOF) {
                if(c == '#') break; 
                if(c == '-' && idx == 0) { 
                    next_c = fgetc(fp);
                    if(next_c == '1') { idx = 0; break; } 
                }
                if((c >= 'A' && c <= 'Z') || c == ' ') {
                    if(idx < 50) buffer[idx++] = c;
                }
            }
            
            // DOC XONG DONG FILE NGAY LAP TUC CHO AN TOAN
            fclose(fp);

            if(idx > 0) {
                buffer[idx] = '\0';
                printf("[DSP] NHAN DUOC LENH: [%s]\n", buffer);
                
                OLED_clear();
                OLED_printString(buffer);
                
                // MO LAI FILE DE GHI -1 VA DONG NGAY LAP TUC
                fp = fopen(CMD_FILE_PATH, "w");
                if(fp) { 
                    fputs("-1", fp); 
                    fclose(fp); 
                }
            }
        }
        delay_ms(100); 
    }
}