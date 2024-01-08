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

class Betelgeuse_Capture(BD):
    board_name = "Betelgeuse"
    bitstream_name = "BetelgeuseNRT"
    
    
    beamformer_balls = [ [ RFMC.ADC.IO_09.Ball, RFMC.ADC.IO_19.Ball ],
                         [ RFMC.ADC.IO_11.Ball, RFMC.ADC.IO_18.Ball ],
                         [ RFMC.ADC.IO_12.Ball, RFMC.ADC.IO_08.Ball ],
                         [ RFMC.ADC.IO_05.Ball, RFMC.ADC.IO_03.Ball ],
                         [ RFMC.DAC.IO_08.Ball, RFMC.DAC.IO_10.Ball ],
                         [ RFMC.DAC.IO_13.Ball, RFMC.DAC.IO_12.Ball ],
                         [ RFMC.DAC.IO_11.Ball, RFMC.DAC.IO_14.Ball ],
                         [ RFMC.DAC.IO_18.Ball, RFMC.DAC.IO_15.Ball ] ]

    txrx_balls = [ RFMC.ADC.IO_14, RFMC.ADC.IO_16, RFMC.ADC.IO_10, RFMC.ADC.IO_07,
                   RFMC.DAC.IO_07, RFMC.ADC.IO_04, RFMC.DAC.IO_16, RFMC.DAC.IO_19 ]

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

        """
startgroup
set_property -dict [list \
  CONFIG.PSU__CRL_APB__PL1_REF_CTRL__FREQMHZ {25} \
  CONFIG.PSU__CRL_APB__PL1_REF_CTRL__SRCSEL {IOPLL} \
  CONFIG.PSU__FPGA_PL1_ENABLE {1} \
] [get_bd_cells ps]
INFO: [PSU-1]  DP_AUDIO clock source: RPLL is also being used by other peripheral clocks. Their outputs may get impacted if any driver changes DP_AUDIO PLL source to support runtime audio change 
endgroup
disconnect_bd_net /aximm0_net [get_bd_pins spi/s_axi_aclk]
connect_bd_net [get_bd_pins ps/pl_clk1] [get_bd_pins spi/s_axi_aclk]
"""
        
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

        #self.jtag_to_axi = JTAGtoAXI(self, "jtag_to_axi", None)

        #self.jtag_to_axi.pins["aclk"].connect(self.ps.pins["pl_clk0"])
        #self.jtag_to_axi.pins["aresetn"].connect(self.ps.pins["pl_resetn0"])

        #self.jtag_to_axi.aximm_overrides = { "clk": "aclk", "rst": "aresetn" }
        
        #self.axi_interconnect.pins["S02_AXI"].connect(self.jtag_to_axi.pins["M_AXI"])
        

        
        print("Creating i2c for clock tree...")
                
        self.i2c_clk = BDI2C(self, "i2c_clk", None)

        i2c_clk_pin = self.i2c_clk.pins["IIC"]

        #i2c_clk_pin.dump_pins()
        
        i2c_clk_port = self.reexport(self.i2c_clk.pins["IIC"], name="IIC_CLK")

        i2c_clk_port.sda_out.set_phys(RFMC.ADC.IO_15.Ball, "LVCMOS18")
        i2c_clk_port.scl_out.set_phys(RFMC.ADC.IO_17.Ball, "LVCMOS18")
        
        self.axi_interconnect.aximm.connect(self.i2c_clk.pins["S_AXI"])

        self.create_gpio()
        
        print("Creating SPI...")
        use_piradspi = False
        
        if use_piradspi:
            self.spi = PiRadSPI(self, "spi", {"CONFIG.C_SPI_SEL_WIDTH": 7})

            #self.spi.dump_properties()
            #self.spi.dump_pins()

            self.axi_interconnect.aximm.connect(self.spi.pins["CSR"])
            self.ps.pl_clk[0].connect(self.spi.pins["io_clk"])

            self.miso = self.reexport(self.spi.pins["miso"])
            self.mosi = self.reexport(self.spi.pins["mosi"])
            self.sclk = self.reexport(self.spi.pins["sclk"])
            csn = self.reexport(self.spi.pins["csn"])

            (self.spi_dev_0, self.spi_dev_1, self.spi_dev_2,
             self.spi_card_0, self.spi_card_1, self.spi_card_en,
             self.locsn) = [ csn[i] for i in range(7) ]
        else:
            print("Using AXI SPI...")

            with open("sources/spimap.v", "w") as f:
                print(spimap_source, file=f)

            self.cmd("add_file sources/spimap.v")

            self.spi_map = BDModule(self, "spi_map", "SPIMAP")

            self.axi_spi = AXI_SPI(self, "spi", { "CONFIG.C_NUM_SS_BITS": 29, "CONFIG.Multiples16": 2 })

            self.axi_spi.pins["ext_spi_clk"].connect(self.ps.pl_clk[0])
            
            self.axi_interconnect.aximm.connect(self.axi_spi.pins["AXI_LITE"])

            self.axi_spi.pins["ss_o"].connect(self.spi_map.pins["csn"])

            self.locsn = self.reexport(self.spi_map.pins["locsn"])
            self.spi_card_en = self.reexport(self.spi_map.pins["spi_card_en"])
            self.spi_card_0 = self.reexport(self.spi_map.pins["spi_card_0"])
            self.spi_card_1 = self.reexport(self.spi_map.pins["spi_card_1"])
            self.spi_dev_0 = self.reexport(self.spi_map.pins["spi_dev_0"])
            self.spi_dev_1 = self.reexport(self.spi_map.pins["spi_dev_1"])
            self.spi_dev_2 = self.reexport(self.spi_map.pins["spi_dev_2"])
            
            self.miso = self.reexport(self.axi_spi.pins["io1_i"])
            self.mosi = self.reexport(self.axi_spi.pins["io0_o"])
            self.sclk = self.reexport(self.axi_spi.pins["sck_o"])
                       
        self.spi_dev_0.set_phys(RFMC.DAC.IO_04.Ball, "LVCMOS18")
        self.spi_dev_1.set_phys(RFMC.DAC.IO_06.Ball, "LVCMOS18")
        self.spi_dev_2.set_phys(RFMC.DAC.IO_09.Ball, "LVCMOS18")
        self.spi_card_0.set_phys(RFMC.DAC.IO_00.Ball, "LVCMOS18")
        self.spi_card_1.set_phys(RFMC.DAC.IO_02.Ball, "LVCMOS18")
        self.spi_card_en.set_phys(RFMC.DAC.IO_17.Ball, "LVCMOS18")
        self.locsn.set_phys(RFMC.ADC.IO_00.Ball, "LVCMOS18")
        
        self.miso.set_phys(RFMC.DAC.IO_03.Ball, "LVCMOS18")
        self.mosi.set_phys(RFMC.DAC.IO_05.Ball, "LVCMOS18")
        self.sclk.set_phys(RFMC.DAC.IO_01.Ball, "LVCMOS18")
            
        self.capture = SampleCapture(self, NCOFreq="1.0")

        for p in self.capture.external_interfaces:
            port = self.reexport(p)
            if p in self.capture.external_clocks:
                port.set_property_list([("CONFIG.FREQ_HZ", "4000000000.0")])

                
        #self.capture.dump_pins()

        self.axi_interconnect.aximm.connect(self.capture.pins["S00_AXI"])
        self.ps.pl_resetn[0].connect(self.capture.pins["ext_reset_in"])

        self.ps.connect_interrupts()


spimap_source = """
module SPIMAP #(
        parameter NCSN = 29
    ) (
    input [NCSN-1:0] csn,
    output spi_dev_0,
    output spi_dev_1,
    output spi_dev_2,
    output spi_card_0,
    output spi_card_1,
    output spi_card_en,
    output locsn
    );
    
    wire [6:0] sel_mask;
    
    // card en card sel 0 card sel 1 dev sel 2 dev sel 1 dev sel 0

    assign spi_dev_0 = sel_mask[0];
    assign spi_dev_1 = sel_mask[1];
    assign spi_dev_2 = sel_mask[2];

    assign spi_card_0 = sel_mask[3];
    assign spi_card_1 = sel_mask[4];

    assign spi_card_en = sel_mask[5];

    assign locsn = sel_mask[6];
    
                      // Card 0
    assign sel_mask = (csn[ 0] == 0) ? 7'b1_1_00_000 :
                      (csn[ 1] == 0) ? 7'b1_1_00_001 :
                      (csn[ 2] == 0) ? 7'b1_1_00_010 :
                      (csn[ 3] == 0) ? 7'b1_1_00_011 :
                      (csn[ 4] == 0) ? 7'b1_1_00_100 :
                      (csn[ 5] == 0) ? 7'b1_1_00_101 :
                      // Card 1
                      (csn[ 6] == 0) ? 7'b1_1_01_000 :
                      (csn[ 7] == 0) ? 7'b1_1_01_001 :
                      (csn[ 8] == 0) ? 7'b1_1_01_010 :
                      (csn[ 9] == 0) ? 7'b1_1_01_011 :
                      (csn[10] == 0) ? 7'b1_1_01_100 :
                      (csn[11] == 0) ? 7'b1_1_01_101 :
                      // Card 2
                      (csn[12] == 0) ? 7'b1_1_10_000 :
                      (csn[13] == 0) ? 7'b1_1_10_001 :
                      (csn[14] == 0) ? 7'b1_1_10_010 :
                      (csn[15] == 0) ? 7'b1_1_10_011 :
                      (csn[16] == 0) ? 7'b1_1_10_100 :
                      (csn[17] == 0) ? 7'b1_1_10_101 :
                      // Card 3
                      (csn[18] == 0) ? 7'b1_1_11_000 :
                      (csn[19] == 0) ? 7'b1_1_11_001 :
                      (csn[20] == 0) ? 7'b1_1_11_010 :
                      (csn[21] == 0) ? 7'b1_1_11_011 :
                      (csn[22] == 0) ? 7'b1_1_11_100 :
                      (csn[23] == 0) ? 7'b1_1_11_101 :
                      // LMX
                      (csn[24] == 0) ? 7'b0_0_00_111 :
                      7'b1_0_00_000;
endmodule
"""

bitstream_definition=Betelgeuse_Capture
