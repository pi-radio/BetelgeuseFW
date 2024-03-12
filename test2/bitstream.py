import sys
import os
from pathlib import Path

modpath = (Path(__file__).parent / ".." / "modules").resolve()

sys.path.insert(0, str(modpath))

from betelgeusefw import *

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import pexpect
import functools
import sys
from functools import cached_property

from piradip.vivado.bd import *

from piradip.rfdc import RFDCReal
from piradip.rfdc.clocking import RFDCClockingMTS


class BetelgeuseTest2(BetelgeuseBD):
    bitstream_name = "BetelgeuseTest2"

    io = BetelgeuseIO

    def __init__(self, t, name):
        super().__init__(t, name, 1)

        reclock_adc=True
        sample_freq=4096e6        

        n_dac_tiles = 2
        n_dac_dc_per_tile = 4
        
        n_adc_tiles = 4
        n_adc_dc_per_tile = 2

        # Filter
        n_dac_axi_units = 1

        # No units
        n_adc_axi_units = 0

        self.aximm_aclk = self.axi_interconnect.pins["ACLK"]
        self.aximm_aresetn = self.axi_interconnect.pins["ARESETN"]
        self.resetn = self.ps.pins["pl_resetn0"]
        
        self.axi_dc_root = AXIInterconnect(self, "axi_fabric", num_masters=n_dac_tiles + 1 + 16 + 1,
                                           global_master_clock=self.aximm_aclk,
                                           global_master_reset=self.aximm_aresetn)            

        self.aximm_aclk.connect(self.axi_dc_root.pins["ACLK"])
        self.aximm_aresetn.connect(self.axi_dc_root.pins["ARESETN"])        
        self.axi_interconnect.aximm.connect(self.axi_dc_root.pins["S00_AXI"])

        
        self.axi_dac_tiles = [ AXIInterconnect(self, f"axi_fabric_dac{i}",
                                               manager_regslice=True,
                                               num_masters=n_dac_dc_per_tile * n_dac_axi_units,
                                               global_master_clock=self.aximm_aclk,
                                               global_master_reset=self.aximm_aresetn)
                               for i in range(n_dac_tiles) ]


        
        
        for adt in self.axi_dac_tiles:            
            adt.pins["ACLK"].connect(self.aximm_aclk)
            adt.pins["ARESETN"].connect(self.aximm_aresetn)

            self.axi_dc_root.aximm.connect(adt.pins["S00_AXI"])
            

            
        #
        # Create IP blocks
        #
        print("Creating RFDC block...")
        self.rfdc = RFDCReal(self, "rfdc", sample_freq=sample_freq, reclock_adc=reclock_adc, clocking=RFDCClockingMTS)

        self.RFDC_reset = self.out_slice32.get_pin()
        
        self.RFDC_reset.connect(self.rfdc.resetn)

        clocking = self.rfdc.clocking
        
        self.in2_concat32.get_pin().connect(self.rfdc.clk_locked)
        self.in2_concat32.get_pin().connect(self.rfdc.clk_stopped)
        self.in2_concat32.get_pin().connect(self.rfdc.clk_fb_stopped)        
        self.in2_concat32.get_pin().connect(self.rfdc.pins["axis_aresetn"])
        
        self.filter_out = [
            AXIS_FIR7SYM_16WIDE(self,
                                f"filter_out{i}",
                                { "CONFIG.STREAM_IN_WIDTH": "256",
                                  "CONFIG.STREAM_OUT_WIDTH": "256" })
            for i in range(8)
        ]

        self.broadcasters = [
            AXISBroadcaster(self,
                            f"broadcaster{i}",
                            { 
                                "CONFIG.S_TDATA_NUM_BYTES.VALUE_SRC": "USER",
                                "CONFIG.M_TDATA_NUM_BYTES.VALUE_SRC": "USER",
                                "CONFIG.M_TDATA_NUM_BYTES": "32",
                                "CONFIG.S_TDATA_NUM_BYTES": "32"                                
                            })
            for i in range(8)
        ]

        self.sample_in = [
            SampleBufferIn(self, f"samples_in{i}", 256,
                           nwords=32768) for i in range(8)
        ]

        self.trigger = TriggerUnit(self, "trigger", None)
        self.slice32 = Slice32(self, "trigger_slice", None)

        self.axi_dc_root.aximm.connect(self.trigger.pins["AXILITE"])
        
        self.connect(self.trigger.pins["triggers"], self.slice32.pins["din"])

        for i in range(8):
            self.connect(self.slice32.pins[f"dout{i}"], self.sample_in[i].pins["trigger"])

        
        # CONFIG.IS_ACLK_ASYNC {1}

        dc_pairs = list(zip(self.adc_map, self.dac_map))

        port_pairs = zip(dc_pairs[0::2], dc_pairs[1::2])

        def connect_channel(n, adcn, dacn):
            adc_clk = self.rfdc.adc_axis_clk[adcn]
            dac_clk = self.rfdc.dac_axis_clk[dacn]

            adc_resetn = self.rfdc.adc_axis_resetn[adcn]
            dac_resetn = self.rfdc.dac_axis_resetn[dacn]

            broad = self.broadcasters[dacn]
            sbi = self.sample_in[dacn]
            
            broad.pins["aclk"].connect(adc_clk)
            broad.pins["aresetn"].connect(adc_resetn)

            broad.pins["S_AXIS"].connect(self.rfdc.adc_axis[adcn])


            sbi.pins["STREAM_IN"].connect(broad.pins["M01_AXIS"])
            sbi.pins["stream_in_clk"].connect(dac_clk)
            sbi.pins["stream_in_resetn"].connect(dac_resetn)
            
            self.axi_dc_root.aximm.connect(sbi.pins["AXILITE"])
            self.axi_dc_root.aximm.connect(sbi.pins["AXIMM"])
            
            self.filter_out[dacn].pins["STREAM_IN"].connect(broad.pins["M00_AXIS"])
            self.filter_out[dacn].pins["STREAM_OUT"].connect(self.rfdc.dac_axis[dacn])
            self.filter_out[dacn].pins["stream_in_clk"].connect(dac_clk)
            self.filter_out[dacn].pins["stream_in_resetn"].connect(dac_resetn)
            self.filter_out[dacn].pins["stream_out_clk"].connect(dac_clk)
            self.filter_out[dacn].pins["stream_out_resetn"].connect(dac_resetn)
        
        for n, ((adcn1, dacn1), (adcn2, dacn2)) in enumerate(port_pairs):
            #
            # Connect ADC 1 to DAC 2
            #
            connect_channel(n, adcn1, dacn2)
            
            #
            # Connect ADC 2 to DAC 1
            #
            connect_channel(n, adcn2, dacn1)

            
        
        self.axi_dc_root.aximm.connect(self.rfdc.pins["S_AXI"])
        
        dtl = [ self.axi_dac_tiles[i] for i in range(n_dac_tiles) for j in range(n_dac_dc_per_tile) ]

        for adt, fo in zip(dtl, self.filter_out):
            adt.aximm.connect(fo.pins["AXILITE"])

        
        #self.rfdc.ext_reset_in.connect(self.resetn)

        for p in self.rfdc.adc_clk + self.rfdc.dac_clk:
            np = self.reexport(p)
            np.set_property_list([("CONFIG.FREQ_HZ", "4096000000.0")])

        for p in self.rfdc.adc_in + self.rfdc.dac_out:
            np = self.reexport(p)


            
            

bitstream_definition=BetelgeuseTest2
