#include <stdio.h>
#include <string.h>
#include "ezdsp5535.h"
#include "oled_display.h"

/* Duong dan file cua JTAG */
#define CMD_FILE_PATH "E:\\KTVT\\setup_CCS_4.2.5.00005\\setup_CCS_4.2.5.00005\\ezdsp5535_BSL_RevC\\ezdsp5535_v1\\tests\\lcd-osd9616\\temp\\cmd.txt"

static void delay_ms(Uint32 ms) {
    volatile Uint32 i, j;
    for (i = 0; i < ms; i++) for (j = 0; j < 2000; j++); 
}

void main(void)
{
    FILE *fp;
    char buffer[60];
    int i = 0;
    char c;

    /* Khoi tao phan cung */
    EZDSP5535_init();
    OLED_init();
    OLED_clear();

    printf("\n=== DSP Dang cho chuoi ky tu tu Python ===\n");

    while(1)
    {
        fp = fopen(CMD_FILE_PATH, "r");
        if (fp != NULL)
        {
            i = 0;
            memset(buffer, 0, sizeof(buffer));

            /* Doc tung ky tu cho den khi gap '#' */
            while ((c = fgetc(fp)) != EOF)
            {
                if (c == '#') break; /* # la ky tu ket thuc cau */
                
                /* Chi lay chu cai in hoa va khoang trang (bo qua cac ky tu khac de font khong bi loi) */
                if ((c >= 'A' && c <= 'Z') || c == ' ') {
                    if (i < 50) { 
                        buffer[i++] = c;
                    }
                }
            }
            fclose(fp);

            /* Neu buffer co du lieu (co nguoi noi) */
            if (i > 0)
            {
                buffer[i] = '\0'; /* Null-terminate chuoi C */
                printf("Da nhan chuoi: %s (Do dai: %d)\n", buffer, i);
                
                /* Xoa sach man hinh hien tai truoc khi in ket qua moi */
                OLED_clear();

                /* Kiem tra dieu kien vuot qua 20 ky tu */
                if (i > 20) {
                    printf("-> CANH BAO: Loi vuot qua 20 ky tu!\n");
                    OLED_printString("QUA GIOI HAN 20!");
                } else {
                    /* In ra OLED binh thuong */
                    OLED_printString(buffer);
                }

                /* Xoa du lieu file de tranh lap lai hien thi tren OLED */
                fp = fopen(CMD_FILE_PATH, "w");
                if (fp != NULL) {
                    fputs("-1", fp);
                    fclose(fp);
                }
            }
        }
        
        /* Ngi 100ms de nhe tai JTAG */
        delay_ms(100); 
    }
}