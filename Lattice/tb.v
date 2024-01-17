`timescale 1ns/1ps

module BGTB;
  reg ctrl_sclk;
  
  wire [7:0] pwr_en;
  
  BetelgeuseTop dut(.sspi_sclk(ctrl_sclk),
	.pwr_en(pwr_en));
  
  
  initial 
  begin
	  ctrl_sclk <= 1'b0;
  end
endmodule
