from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import pexpect
import functools
import sys
from functools import cached_property


from piradip.vivado.bd import *

from .io import BetelgeuseIO

class BetelgeuseBD(BD):
    board_name = "Betelgeuse"

    io = BetelgeuseIO

    _adc_map = [ 4, 7, 3, 0, 6, 5, 1, 2 ]
    _dac_map = [ 1, 0, 4, 5, 3, 2, 6, 7 ]

    @property
    def adc_map(self):
        return self._adc_map
    
    @property
    def dac_map(self):
        return self._dac_map
    
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
    
    def __init__(self, t, name, num_periph):
        super().__init__(t, name)

        print("Creating Zynq UltraScale(TM) Processing System cell...")
                
        self.ps = Zynq_US_PS(self, "ps")

        self.ps.setup_aximm()

        print("Creating AXI Interconnect...")

        #
        # 3 control peripherals -- Control SPI, AMP spi and GPIO
        #
        
        self.axi_interconnect = AXIInterconnect(self, "axi_interconnect",
                                                num_subordinates=2,
                                                num_managers=3 + num_periph,
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
        
        self.gpio = GPIO(self, "pl_gpio", dual=True)
        self.out_slice32 = Slice32(self, "gpio_slice_out", None)
        self.in_concat32 = Concat32(self, "gpio_concat_in", None)
        self.out2_slice32 = Slice32(self, "gpio2_slice_out", None)
        self.in2_concat32 = Concat32(self, "gpio2_concat_in", None)
        
        self.axi_interconnect.aximm.connect(self.gpio.pins["S_AXI"])
        
        self.connect(self.gpio.pins["gpio_io_o"], self.out_slice32.pins["din"])
        self.connect(self.gpio.pins["gpio_io_i"], self.in_concat32.pins["dout"])
        self.connect(self.gpio.pins["gpio2_io_o"], self.out2_slice32.pins["din"])
        self.connect(self.gpio.pins["gpio2_io_i"], self.in2_concat32.pins["dout"])
        
        output_pins = [ 'PWR_ENABLE', 'PROGRAMN', 'JTAGEN',
                        'AMPCH0', 'AMPCH1', 'AMPCH2', 'AMPCH3',
                        'AMPCH4', 'AMPCH5', 'AMPCH6', 'AMPCH7',
                        'AMPCS0', 'AMPCS1', 'AMPCS2',
                        'PWREN0', 'PWREN1', 'PWREN2', 'PWREN3',
                        'PWREN4', 'PWREN5', 'PWREN6', 'PWREN7',
                        'R3', 'P9', 'R12', 'R6'
        ]
        
        for i, pin_name in enumerate(output_pins):
            pin = self.out_slice32.get_pin()
            
            self.reexport(pin).set_phys(self.io.balls[pin_name], "LVCMOS18")

        for i, pin_name in enumerate(['INITN', 'DONE', 'P8', 'R4', 'P7', 'T3']):
            pin = self.in2_concat32.get_pin()
            
            self.reexport(pin).set_phys(self.io.balls[pin_name], "LVCMOS18")
