
module BetelgeuseTop 
(
 input wire sspi_csn,
 input wire sspi_sclk,
 input wire sspi_mosi,
 output wire sspi_miso,

 input wire ampspi_csn,
 input wire ampspi_sclk,
 input wire ampspi_mosi,
 output wire ampspi_miso,
 
 output wire spi1_sclk,
 output wire spi1_mosi,
 input wire spi1_miso,
 output wire spi1_adc_vga_csn,
 output wire spi1_dac_vga1_csn,
 output wire spi1_dac_vga2_csn,
 
 output wire spi2_sclk,
 output wire spi2_mosi,
 input wire spi2_miso,
 output wire spi2_adc_vga_csn,
 output wire spi2_dac_vga1_csn,
 output wire spi2_dac_vga2_csn,
 
 output wire spi3_sclk,
 output wire spi3_mosi,
 input wire spi3_miso,
 output wire spi3_adc_vga_csn,
 output wire spi3_dac_vga1_csn,
 output wire spi3_dac_vga2_csn,
 
 output wire spi4_sclk,
 output wire spi4_mosi,
 input wire spi4_miso,
 output wire spi4_adc_vga_csn,
 output wire spi4_dac_vga1_csn,
 output wire spi4_dac_vga2_csn,
 
 output wire spi5_sclk,
 output wire spi5_mosi,
 input wire spi5_miso,
 output wire spi5_adc_vga_csn,
 output wire spi5_dac_vga1_csn,
 output wire spi5_dac_vga2_csn,
 
 output wire spi6_sclk,
 output wire spi6_mosi,
 input wire spi6_miso,
 output wire spi6_adc_vga_csn,
 output wire spi6_dac_vga1_csn,
 output wire spi6_dac_vga2_csn,
 
 output wire spi7_sclk,
 output wire spi7_mosi,
 input wire spi7_miso,
 output wire spi7_adc_vga_csn,
 output wire spi7_dac_vga1_csn,
 output wire spi7_dac_vga2_csn,
 
 output wire spi8_sclk,
 output wire spi8_mosi,
 input wire spi8_miso,
 output wire spi8_adc_vga_csn,
 output wire spi8_dac_vga1_csn,
 output wire spi8_dac_vga2_csn,
 
 output wire pwr_en0,
 output wire pwr_en1,
 output wire pwr_en2,
 output wire pwr_en3,
 output wire pwr_en4,
 output wire pwr_en5,
 output wire pwr_en6,
 output wire pwr_en7,

 output wire led1,
 output wire led2,
 output wire led3,
 output wire led4
);

  wire [3:0] leds;
  wire [7:0] pwr_en;
  wire [7:0] ampspi_chsel;
  wire [2:0] ampspi_chipsel;
  
  wire       wb_clk;
  wire       wb_rst;
  wire       wb_cyc;
  wire       wb_stb;
  wire       wb_we;
  wire [7:0] wb_adr;
  wire [7:0] wb_dati;
  wire [7:0] wb_dato;
  wire       wb_ack; 


  wire [7:0] address;
  wire       wr_en, rd_en;
  wire [7:0] wr_data;
  wire [7:0] rd_data;
  wire xfer_done;
  wire xfer_req;

  wire spi_irq;

  wire osc_clk;


  assign ampspi_miso = (ampspi_chsel & 8'h01) ? spi1_miso :
		       (ampspi_chsel & 8'h02) ? spi2_miso :
		       (ampspi_chsel & 8'h04) ? spi3_miso :
		       (ampspi_chsel & 8'h08) ? spi4_miso :
		       (ampspi_chsel & 8'h10) ? spi5_miso :
		       (ampspi_chsel & 8'h20) ? spi6_miso :
		       (ampspi_chsel & 8'h40) ? spi7_miso :
		       (ampspi_chsel & 8'h80) ? spi8_miso : 1'b1;
  
  assign spi1_sclk = (ampspi_chsel & 8'h01) ? ampspi_sclk : 1'b1;
  assign spi1_mosi = (ampspi_chsel & 8'h01) ? ampspi_mosi : 1'b1;
  assign spi1_adc_vga_csn = ((ampspi_chsel & 8'h01) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi1_dac_vga1_csn = ((ampspi_chsel & 8'h01) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi1_dac_vga2_csn = ((ampspi_chsel & 8'h01) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

  assign spi2_sclk = (ampspi_chsel & 8'h02) ? ampspi_sclk : 1'b1;
  assign spi2_mosi = (ampspi_chsel & 8'h02) ? ampspi_mosi : 1'b1;
  assign spi2_adc_vga_csn = ((ampspi_chsel & 8'h02) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi2_dac_vga1_csn = ((ampspi_chsel & 8'h02) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi2_dac_vga2_csn = ((ampspi_chsel & 8'h02) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

  assign spi3_sclk = (ampspi_chsel & 8'h04) ? ampspi_sclk : 1'b1;
  assign spi3_mosi = (ampspi_chsel & 8'h04) ? ampspi_mosi : 1'b1;
  assign spi3_adc_vga_csn = ((ampspi_chsel & 8'h04) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi3_dac_vga1_csn = ((ampspi_chsel & 8'h04) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi3_dac_vga2_csn = ((ampspi_chsel & 8'h04) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

  assign spi4_sclk = (ampspi_chsel & 8'h08) ? ampspi_sclk : 1'b1;
  assign spi4_mosi = (ampspi_chsel & 8'h08) ? ampspi_mosi : 1'b1;
  assign spi4_adc_vga_csn = ((ampspi_chsel & 8'h08) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi4_dac_vga1_csn = ((ampspi_chsel & 8'h08) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi4_dac_vga2_csn = ((ampspi_chsel & 8'h08) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;
  
  assign spi5_sclk = (ampspi_chsel & 8'h10) ? ampspi_sclk : 1'b1;
  assign spi5_mosi = (ampspi_chsel & 8'h10) ? ampspi_mosi : 1'b1;
  assign spi5_adc_vga_csn = ((ampspi_chsel & 8'h10) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi5_dac_vga1_csn = ((ampspi_chsel & 8'h10) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi5_dac_vga2_csn = ((ampspi_chsel & 8'h10) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;
  
  assign spi6_sclk = (ampspi_chsel & 8'h20) ? ampspi_sclk : 1'b1;
  assign spi6_mosi = (ampspi_chsel & 8'h20) ? ampspi_mosi : 1'b1;
  assign spi6_adc_vga_csn = ((ampspi_chsel & 8'h20) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi6_dac_vga1_csn = ((ampspi_chsel & 8'h20) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi6_dac_vga2_csn = ((ampspi_chsel & 8'h20) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

  assign spi7_sclk = (ampspi_chsel & 8'h40) ? ampspi_sclk : 1'b1;
  assign spi7_mosi = (ampspi_chsel & 8'h40) ? ampspi_mosi : 1'b1;
  assign spi7_adc_vga_csn = ((ampspi_chsel & 8'h40) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi7_dac_vga1_csn = ((ampspi_chsel & 8'h40) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi7_dac_vga2_csn = ((ampspi_chsel & 8'h40) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

  assign spi8_sclk = (ampspi_chsel & 8'h80) ? ampspi_sclk : 1'b1;
  assign spi8_mosi = (ampspi_chsel & 8'h80) ? ampspi_mosi : 1'b1;
  assign spi8_adc_vga_csn = ((ampspi_chsel & 8'h80) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
  assign spi8_dac_vga1_csn = ((ampspi_chsel & 8'h80) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
  assign spi8_dac_vga2_csn = ((ampspi_chsel & 8'h80) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;
  
  assign pwr_en0 = pwr_en[0];
  assign pwr_en1 = pwr_en[1];
  assign pwr_en2 = pwr_en[2];
  assign pwr_en3 = pwr_en[3];
  assign pwr_en4 = pwr_en[4];
  assign pwr_en5 = pwr_en[5];
  assign pwr_en6 = pwr_en[6];
  assign pwr_en7 = pwr_en[7];

  assign led1 = leds[0];
  assign led2 = leds[1];
  assign led3 = leds[2];
  assign led4 = leds[3];
  
  
  OSCH OSCH_inst(.STDBY(1'b0),
		 .OSC(osc_clk),
		 .SEDSTDBY());

  // Internal Oscillator
  // defparam OSCH_inst.NOM_FREQ = "2.08"; // This is the default frequency defparam
  //OSCH_inst.NOM_FREQ = "100";  

  
  assign wb_clk = osc_clk;
  
  spi_efb efb 
    (
     .wb_clk_i(wb_clk), 
     .wb_rst_i(wb_rst),
     .wb_cyc_i(wb_cyc), 
     .wb_stb_i(wb_stb), 
     .wb_we_i(wb_we), 
     .wb_adr_i(wb_adr), 
     .wb_dat_i(wb_dati), 
     .wb_dat_o(wb_dato), 
     .wb_ack_o(wb_ack),
     .spi_clk(sspi_sclk), 
     .spi_miso(sspi_miso), 
     .spi_mosi(sspi_mosi), 
     .spi_scsn(sspi_csn),
     .spi_irq(spi_irq)
     );
  
  wishbone_controller wbctl
    (
     .wb_clk_i(wb_clk),
     .wb_rst_i(wb_rst),
     .wb_cyc_i(wb_cyc),
     .wb_stb_i(wb_stb),
     .wb_we_i(wb_we),
     .wb_adr_i(wb_adr),
     .wb_dat_i(wb_dati),
     .wb_dat_o(wb_dato),
     .wb_ack_o(wb_ack),
     .address(address),
     .wr_en(wr_en),
     .wr_data(wr_data),
     .rd_en(rd_en),
     .rd_data(rd_data),
     .xfer_done(xfer_done),
     .xfer_req(xfer_rq)
     );

  system_spi_subordinate spi_sub
    (   
	.clk(wb_clK),
	.rstn(wb_rst),
	.spi_csn(sspi_csn),
	.spi_irq(spi_irq),
	.wb_xfer_rdy(xfer_rq),
	.wb_xfer_done(xfer_done),
	.rd_en(rd_en),
	.wr_en(wr_en),
	.address(address),
	.wb_read_data(rd_data),
	.wb_write_data(wr_dat),
	.pwr_en(pwr_en),
	.leds(leds),
	.ampchan(ampspi_chsel),
	.ampcs(ampspi_chipsel)
	);


endmodule
