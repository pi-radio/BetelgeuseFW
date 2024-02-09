from piradip.vivado.bd import *

class BetelgeuseIO:
    balls = {
        'DONE': RFMC.DAC.IO_12.Ball,
        'INITN': RFMC.DAC.IO_15.Ball,
        'PROGRAMN': RFMC.DAC.IO_17.Ball,
        'JTAGEN': RFMC.DAC.IO_18.Ball,
        'PWR_ENABLE': RFMC.DAC.IO_19.Ball,
        
        'SSPI_SCLK': RFMC.ADC.IO_09.Ball, # P6
        'SSPI_MOSI': RFMC.ADC.IO_18.Ball, # P13
        'SSPI_MISO': RFMC.ADC.IO_03.Ball, # T6
        'SSPI_CSN': RFMC.ADC.IO_06.Ball, # R5
        
        'AMPSPI_SCLK': RFMC.ADC.IO_00.Ball,
        'AMPSPI_MOSI': RFMC.ADC.IO_01.Ball,
        'AMPSPI_MISO': RFMC.ADC.IO_02.Ball,
        'AMPSPI_CSN': RFMC.ADC.IO_04.Ball,

        
        'AMPCH0': RFMC.ADC.IO_05.Ball,
        'AMPCH1': RFMC.ADC.IO_07.Ball,
        'AMPCH2': RFMC.ADC.IO_08.Ball, 
        'AMPCH3': RFMC.ADC.IO_10.Ball, 
        'AMPCH4': RFMC.ADC.IO_11.Ball,
        'AMPCH5': RFMC.ADC.IO_12.Ball,
        'AMPCH6': RFMC.ADC.IO_13.Ball,
        'AMPCH7': RFMC.ADC.IO_14.Ball,
        'AMPCS0': RFMC.ADC.IO_15.Ball,
        'AMPCS1': RFMC.ADC.IO_16.Ball,
        'AMPCS2': RFMC.ADC.IO_17.Ball,

        'PWREN0': RFMC.ADC.IO_19.Ball,
        'PWREN1': RFMC.DAC.IO_00.Ball,
        'PWREN2': RFMC.DAC.IO_01.Ball,
        'PWREN3': RFMC.DAC.IO_16.Ball,
        'PWREN4': RFMC.DAC.IO_03.Ball,
        'PWREN5': RFMC.DAC.IO_04.Ball,
        'PWREN6': RFMC.DAC.IO_05.Ball,
        'PWREN7': RFMC.DAC.IO_06.Ball,
        
        'R3': RFMC.DAC.IO_07.Ball,
        'P9': RFMC.DAC.IO_08.Ball, 
        'R6': RFMC.DAC.IO_09.Ball, 
        'P8': RFMC.DAC.IO_10.Ball, 
        'R4': RFMC.DAC.IO_11.Ball,
        'P7': RFMC.DAC.IO_13.Ball,
        'T3': RFMC.DAC.IO_14.Ball,
        'R12': RFMC.DAC.IO_02.Ball,

    }
