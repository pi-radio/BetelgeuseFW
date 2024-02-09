import sys
import os
from pathlib import Path

modpath = (Path(__file__).parent / ".." / "modules").resolve()

print(modpath)

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
    
class Betelgeuse_Capture(BetelgeuseBD):
    bitstream_name = "BetelgeuseTest1"

    io = BetelgeuseIO

    def __init__(self, t, name):
        super().__init__(t, name, 0)

        """
        self.axi_interconnect = AXIInterconnect(self, "axi_interconnect",
                                                num_subordinates=2, num_managers=4,
                                                global_clock=self.ps.aximm_clocks[0],
                                                global_reset=self.ps.aximm_clocks[0].assoc_resetn)
        """


        """
        NSAMPLES = 64 * 1024
            
        tx_samples = [ NSAMPLES ] * 8

        rx_samples = [ NSAMPLES ] * 8
        
        self.capture = RealSampleCapture(self, tx_samples=tx_samples, rx_samples=rx_samples, sample_freq=4096e6)

        for p in self.capture.external_interfaces:
            port = self.reexport(p)
            if p in self.capture.external_clocks:
                port.set_property_list([("CONFIG.FREQ_HZ", "4096000000.0")])

                
        #self.capture.dump_pins()

        self.axi_interconnect.aximm.connect(self.capture.pins["S00_AXI"])
        self.ps.pl_resetn[0].connect(self.capture.pins["ext_reset_in"])
        """
        
        #self.ps.connect_interrupts()

bitstream_definition=Betelgeuse_Capture
