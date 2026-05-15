#include "stdio.h"
#include "ezdsp5535.h"
#include "ezdsp5535_i2s.h"

extern Int16 AIC3204_rset( Uint16 regnum, Uint16 regval);

void Setup_AIC3204_Record(void)
{
    printf("[INIT] Bat dau Setup_AIC3204_Record...\n");

    /* Configure AIC3204 - COPY NGUYEN XI TU aic3204_loop_linein.c (TI chinh thuc) */
    AIC3204_rset( 0,   0x00 );  // Select page 0
    AIC3204_rset( 1,   0x01 );  // Reset codec
    EZDSP5535_waitusec(1000);   // Wait 1ms after reset
    AIC3204_rset( 0,   0x01 );  // Select page 1
    AIC3204_rset( 1,   0x08 );  // Disable crude AVDD generation from DVDD
    AIC3204_rset( 2,   0x01 );  // Enable Analog Blocks, use LDO power
    AIC3204_rset( 123, 0x05 );  // Force reference to power up in 40ms
    EZDSP5535_waitusec(50000);  // Wait at least 40ms
    AIC3204_rset( 0,   0x00 );  // Select page 0
    printf("[INIT] Analog power OK.\n");

    /* PLL and Clocks - NGUYEN XI TU TI SAMPLE */
    AIC3204_rset( 27,  0x0d );  // BCLK and WCLK as output; AIC3204 = Master
    AIC3204_rset( 28,  0x00 );  // Data offset = 0
    AIC3204_rset( 4,   0x03 );  // PLL: PLLCLK <- MCLK, CODEC_CLKIN <- PLL CLK
    AIC3204_rset( 6,   0x07 );  // PLL: J=7
    AIC3204_rset( 7,   0x06 );  // PLL: HI_BYTE(D=1680)
    AIC3204_rset( 8,   0x90 );  // PLL: LO_BYTE(D=1680)
    AIC3204_rset( 30,  0x88 );  // BCLK=DAC_CLK/N, 32 bit clocks per frame (Master)
    AIC3204_rset( 5,   0x91 );  // PLL: Power up, P=1, R=1
    EZDSP5535_waitusec(10000);  // Wait for PLL
    AIC3204_rset( 13,  0x00 );  // DOSR=128 HI
    AIC3204_rset( 14,  0x80 );  // DOSR=128 LO
    AIC3204_rset( 20,  0x80 );  // AOSR=128
    AIC3204_rset( 11,  0x82 );  // NDAC=2, powered
    AIC3204_rset( 12,  0x87 );  // MDAC=7, powered
    AIC3204_rset( 18,  0x87 );  // NADC=7, powered
    AIC3204_rset( 19,  0x82 );  // MADC=2, powered
    printf("[INIT] Clock OK.\n");

    /* DAC Routing - can thiet de AIC3204 generate BCLK lien tuc */
    AIC3204_rset( 0,   0x01 );  // Select page 1
    AIC3204_rset( 12,  0x08 );  // LDAC -> HPL
    AIC3204_rset( 13,  0x08 );  // RDAC -> HPR
    AIC3204_rset( 0,   0x00 );  // Select page 0
    AIC3204_rset( 64,  0x02 );  // Left vol = right vol
    AIC3204_rset( 65,  0x00 );  // DAC gain 0dB
    AIC3204_rset( 63,  0xd4 );  // Power up L+R DAC
    AIC3204_rset( 0,   0x01 );  // Select page 1
    AIC3204_rset( 16,  0x00 );  // Unmute HPL, 0dB
    AIC3204_rset( 17,  0x00 );  // Unmute HPR, 0dB
    AIC3204_rset( 9,   0x30 );  // Power up HPL, HPR
    EZDSP5535_waitusec(100);
    printf("[INIT] DAC OK.\n");

    /* ADC Routing - Stereo Line In (IN2_L/R) */
    AIC3204_rset( 0,   0x01 );  // Select page 1
    AIC3204_rset( 52,  0x30 );  // IN2_L -> LADC_P (40k)
    AIC3204_rset( 55,  0x30 );  // IN2_R -> RADC_P (40k)
    AIC3204_rset( 54,  0x03 );  // CM_1 -> LADC_M (40k)
    AIC3204_rset( 57,  0xc0 );  // CM_1 -> RADC_M (40k)
    AIC3204_rset( 59,  0x00 );  // MIC_PGA_L unmute
    AIC3204_rset( 60,  0x00 );  // MIC_PGA_R unmute
    AIC3204_rset( 0,   0x00 );  // Select page 0
    AIC3204_rset( 81,  0xc0 );  // Power up L+R ADC
    AIC3204_rset( 82,  0x00 );  // Unmute L+R ADC
    AIC3204_rset( 0,   0x00 );  // Select page 0
    EZDSP5535_waitusec(100);
    printf("[INIT] ADC OK.\n");

    /* Initialize I2S */
    EZDSP5535_I2S_init();
    printf("[INIT] I2S OK. Setup HOAN TAT.\n");
}