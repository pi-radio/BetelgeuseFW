from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os.path
from pathlib import Path
import pexpect
import functools
import sys
from functools import cached_property

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

        
        'T9': RFMC.ADC.IO_05.Ball,
        'T10': RFMC.ADC.IO_07.Ball,
        'T11': RFMC.ADC.IO_08.Ball, 
        'T12': RFMC.ADC.IO_10.Ball, 
        'P10': RFMC.ADC.IO_11.Ball,
        'R13': RFMC.ADC.IO_12.Ball,
        'P12': RFMC.ADC.IO_13.Ball,
        'P11': RFMC.ADC.IO_14.Ball,
        'T13': RFMC.ADC.IO_15.Ball,
        'R14': RFMC.ADC.IO_16.Ball,
        'T14': RFMC.ADC.IO_17.Ball,
        'T15': RFMC.ADC.IO_19.Ball,

        'R11': RFMC.DAC.IO_00.Ball,
        'R9': RFMC.DAC.IO_01.Ball,
        'R12': RFMC.DAC.IO_02.Ball,
        'R10': RFMC.DAC.IO_03.Ball,
        'R8': RFMC.DAC.IO_04.Ball,
        'P4': RFMC.DAC.IO_05.Ball,
        'R7': RFMC.DAC.IO_06.Ball,
        'R3': RFMC.DAC.IO_07.Ball,
        'P9': RFMC.DAC.IO_08.Ball, 
        'R6': RFMC.DAC.IO_09.Ball, 
        'P8': RFMC.DAC.IO_10.Ball, 
        'R4': RFMC.DAC.IO_11.Ball,
        'P7': RFMC.DAC.IO_13.Ball,
        'T3': RFMC.DAC.IO_14.Ball,
        'T2': RFMC.DAC.IO_16.Ball,
    }
    
class Betelgeuse_Capture(BD):
    board_name = "Betelgeuse"
    bitstream_name = "BetelgeuseNRT"

    io = BetelgeuseIO

    def create_gpio(self):
        print("Creating GPIO...")
        
        self.gpio = GPIO(self, "pl_gpio")
        self.slice32 = Slice32(self, "gpio_slice", None)
        
        self.axi_interconnect.aximm.connect(self.gpio.pins["S_AXI"])
        
        self.connect(self.gpio.pins["gpio_io_o"], self.slice32.pins["din"])
        
        self.rst_out = self.reexport(self.slice32.pins["dout0"])
        
        self.rst_out.set_phys(RFMC.ADC.IO_01.Ball, "LVCMOS18")
        
        self.bf = [ [ self.reexport(self.slice32.pins[f"dout{1+2*i+j}"]) for j in range(2) ] for i in range(8) ] 
        
        for ports, balls in zip(self.bf, self.beamformer_balls):
            for port, ball in zip(ports, balls):
                port.set_phys(ball, "LVCMOS18")
    
    def __init__(self, t, name):
        super().__init__(t, name)


        print("Creating Zynq UltraScale(TM) Processing System cell...")
                
        self.ps = Zynq_US_PS(self, "ps")

        self.ps.setup_aximm()

        print("Creating AXI Interconnect...")

        self.axi_interconnect = AXIInterconnect(self, "axi_interconnect",
                                                num_subordinates=2, num_managers=4,
                                                global_clock=self.ps.aximm_clocks[0],
                                                global_reset=self.ps.aximm_clocks[0].assoc_resetn)

        self.ps.pl_clk[0].connect(self.axi_interconnect.pins["ACLK"])
        self.ps.pl_clk[0].assoc_resetn.connect(self.axi_interconnect.pins["ARESETN"])
        
        self.axi_interconnect.pins["S00_AXI"].connect(self.ps.pins["M_AXI_HPM0_FPD"])
        self.axi_interconnect.pins["S01_AXI"].connect(self.ps.pins["M_AXI_HPM1_FPD"])

                
        print("Ceating Control AXI SPI...")

        self.ctrl_axi_spi = AXI_SPI(self, "ctrl_spi", { "CONFIG.C_NUM_SS_BITS": 1, "CONFIG.Multiples16": 2 })

        self.ctrl_axi_spi.pins["ext_spi_clk"].connect(self.ps.pl_clk[0])
            
        self.axi_interconnect.aximm.connect(self.ctrl_axi_spi.pins["AXI_LITE"])

        self.ctrl_csn = self.reexport(self.ctrl_axi_spi.pins["ss_o"], "ctrl_csn")
        self.ctrl_miso = self.reexport(self.ctrl_axi_spi.pins["io1_i"], "ctrl_miso")
        self.ctrl_mosi = self.reexport(self.ctrl_axi_spi.pins["io0_o"], "ctrl_mosi")
        self.ctrl_sclk = self.reexport(self.ctrl_axi_spi.pins["sck_o"], "ctrl_sck")

        self.ctrl_csn.set_phys(self.io.balls['SSPI_CSN'], "LVCMOS18")
        self.ctrl_miso.set_phys(self.io.balls['SSPI_MISO'], "LVCMOS18")
        self.ctrl_mosi.set_phys(self.io.balls['SSPI_MOSI'], "LVCMOS18")
        self.ctrl_sclk.set_phys(self.io.balls['SSPI_SCLK'], "LVCMOS18")

        self.amp_axi_spi = AXI_SPI(self, "amp_spi", { "CONFIG.C_NUM_SS_BITS": 1, "CONFIG.Multiples16": 2 })

        self.amp_axi_spi.pins["ext_spi_clk"].connect(self.ps.pl_clk[0])
            
        self.axi_interconnect.aximm.connect(self.amp_axi_spi.pins["AXI_LITE"])

        self.amp_csn = self.reexport(self.amp_axi_spi.pins["ss_o"], "amp_csn")
        self.amp_miso = self.reexport(self.amp_axi_spi.pins["io1_i"], "amp_miso")
        self.amp_mosi = self.reexport(self.amp_axi_spi.pins["io0_o"], "amp_mosi")
        self.amp_sclk = self.reexport(self.amp_axi_spi.pins["sck_o"], "amp_sck")

        self.amp_csn.set_phys(self.io.balls['AMPSPI_CSN'], "LVCMOS18")
        self.amp_miso.set_phys(self.io.balls['AMPSPI_MISO'], "LVCMOS18")
        self.amp_mosi.set_phys(self.io.balls['AMPSPI_MOSI'], "LVCMOS18")
        self.amp_sclk.set_phys(self.io.balls['AMPSPI_SCLK'], "LVCMOS18")


        print("Creating GPIO...")
        
        self.gpio = GPIO(self, "pl_gpio")
        self.out_slice32 = Slice32(self, "gpio_slice_out", None)
        self.in_concat32 = Concat32(self, "gpio_concat_in", None)
        
        self.axi_interconnect.aximm.connect(self.gpio.pins["S_AXI"])
        
        self.connect(self.gpio.pins["gpio_io_o"], self.out_slice32.pins["din"])
        self.connect(self.gpio.pins["gpio_io_i"], self.in_concat32.pins["dout"])
        
        for i, pin_name in enumerate(['PWR_ENABLE', 'PROGRAMN', 'JTAGEN']):
            self.reexport(self.out_slice32.pins[f"dout{i}"]).set_phys(self.io.balls[pin_name], "LVCMOS18")
        
        for i, pin_name in enumerate(['INITN', 'DONE']):
            self.reexport(self.in_concat32.pins[f"din{i}"]).set_phys(self.io.balls[pin_name], "LVCMOS18")


        
        
        self.capture = SampleCapture(self, NCOFreq="0.0")

        for p in self.capture.external_interfaces:
            port = self.reexport(p)
            if p in self.capture.external_clocks:
                port.set_property_list([("CONFIG.FREQ_HZ", "4000000000.0")])

                
        #self.capture.dump_pins()

        self.axi_interconnect.aximm.connect(self.capture.pins["S00_AXI"])
        self.ps.pl_resetn[0].connect(self.capture.pins["ext_reset_in"])

        self.ps.connect_interrupts()

bitstream_definition=Betelgeuse_Capture
