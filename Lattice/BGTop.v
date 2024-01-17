
module BetelgeuseTop 
(
 inout wire sspi_sclk,
 inout wire sspi_miso,
 inout wire sspi_mosi,
 input wire sspi_csn,

 input wire ampspi_csn,
 input wire ampspi_sclk,
 input wire ampspi_mosi,
 output reg ampspi_miso,
 
 output reg spi1_sclk,
 output reg spi1_mosi,
 input wire spi1_miso,
 output reg spi1_adc_vga_csn,
 output reg spi1_dac_vga1_csn,
 output reg spi1_dac_vga2_csn,
 
 output reg spi2_sclk,
 output reg spi2_mosi,
 input wire spi2_miso,
 output reg spi2_adc_vga_csn,
 output reg spi2_dac_vga1_csn,
 output reg spi2_dac_vga2_csn,
 
 output reg spi3_sclk,
 output reg spi3_mosi,
 input wire spi3_miso,
 output reg spi3_adc_vga_csn,
 output reg spi3_dac_vga1_csn,
 output reg spi3_dac_vga2_csn,
 
 output reg spi4_sclk,
 output reg spi4_mosi,
 input wire spi4_miso,
 output reg spi4_adc_vga_csn,
 output reg spi4_dac_vga1_csn,
 output reg spi4_dac_vga2_csn,
 
 output reg spi5_sclk,
 output reg spi5_mosi,
 input wire spi5_miso,
 output reg spi5_adc_vga_csn,
 output reg spi5_dac_vga1_csn,
 output reg spi5_dac_vga2_csn,
 
 output reg spi6_sclk,
 output reg spi6_mosi,
 input wire spi6_miso,
 output reg spi6_adc_vga_csn,
 output reg spi6_dac_vga1_csn,
 output reg spi6_dac_vga2_csn,
 
 output reg spi7_sclk,
 output reg spi7_mosi,
 input wire spi7_miso,
 output reg spi7_adc_vga_csn,
 output reg spi7_dac_vga1_csn,
 output reg spi7_dac_vga2_csn,
 
 output reg spi8_sclk,
 output reg spi8_mosi,
 input wire spi8_miso,
 output reg spi8_adc_vga_csn,
 output reg spi8_dac_vga1_csn,
 output reg spi8_dac_vga2_csn,
 
 output reg pwr_en0,
 output reg pwr_en1,
 output reg pwr_en2,
 output reg pwr_en3,
 output reg pwr_en4,
 output reg pwr_en5,
 output reg pwr_en6,
 output reg pwr_en7,

 output wire led1,
 output wire led2,
 output wire led3,
 output wire led4,
 
 input wire ampch0,
 input wire ampch1,
 input wire ampch2,
 input wire ampch3,
 input wire ampch4,
 input wire ampch5,
 input wire ampch6,
 input wire ampch7,
 input wire ampcs0,
 input wire ampcs1,
 input wire ampcs2,

 input wire pwren_i0,
 input wire pwren_i1,
 input wire pwren_i2,
 input wire pwren_i3,
 input wire pwren_i4,
 input wire pwren_i5,
 input wire pwren_i6,
 input wire pwren_i7
 
 //input wire aux1,
 //output wire aux2
);

/*
*/
  wire       osc_clk;

  OSCH OSCH_inst(.STDBY(1'b0),
		 .OSC(osc_clk),
		 .SEDSTDBY());
  // defparam OSCH_inst.NOM_FREQ = "133.0";
  defparam OSCH_inst.NOM_FREQ = "133.0";  
		 
  assign wb_clk = osc_clk;

  reg [7:0] ampspi_chsel;
  reg [2:0] ampspi_chipsel;

  always @(posedge osc_clk) begin
	ampspi_chipsel <= { ~ampcs2, ~ampcs1, ~ampcs0 };
	ampspi_chsel <= { ampch7, ampch6, ampch5, ampch4,
					   ampch3, ampch2, ampch1, ampch0 };
	pwr_en0 <= pwren_i0;
	pwr_en1 <= pwren_i1;
	pwr_en2 <= pwren_i2;
	pwr_en3 <= pwren_i3;
	pwr_en4 <= pwren_i4;
	pwr_en5 <= pwren_i5;
	pwr_en6 <= pwren_i6;
	pwr_en7 <= pwren_i7;
  end
  
  always @(posedge osc_clk) 
  begin
	ampspi_miso <= (ampspi_chsel & 8'h01) ? spi1_miso :
					(ampspi_chsel & 8'h02) ? spi2_miso :
					(ampspi_chsel & 8'h04) ? spi3_miso :
					(ampspi_chsel & 8'h08) ? spi4_miso :
				    (ampspi_chsel & 8'h10) ? spi5_miso :
		            (ampspi_chsel & 8'h20) ? spi6_miso :
		            (ampspi_chsel & 8'h40) ? spi7_miso :
		            (ampspi_chsel & 8'h80) ? spi8_miso : 1'b1;
  end			   
			   
  wire [7:0] ampsclk;
  wire [7:0] ampmosi;
  wire [7:0] ampmiso;
  wire [7:0] adc_vga_csn;
  wire [7:0] dac_vga1_csn;
  wire [7:0] dac_vga2_csn;

	
  
  always @(posedge osc_clk)
  begin
	spi1_sclk <= (ampspi_chsel & 8'h01) ? ampspi_sclk : 1'b1;
    spi1_mosi <= (ampspi_chsel & 8'h01) ? ampspi_mosi : 1'b1;
    spi1_adc_vga_csn <= ((ampspi_chsel & 8'h01) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi1_dac_vga1_csn <= ((ampspi_chsel & 8'h01) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi1_dac_vga2_csn <= ((ampspi_chsel & 8'h01) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

    spi2_sclk <= (ampspi_chsel & 8'h02) ? ampspi_sclk : 1'b1;
    spi2_mosi <= (ampspi_chsel & 8'h02) ? ampspi_mosi : 1'b1;
    spi2_adc_vga_csn <= ((ampspi_chsel & 8'h02) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi2_dac_vga1_csn <= ((ampspi_chsel & 8'h02) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi2_dac_vga2_csn <= ((ampspi_chsel & 8'h02) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

    spi3_sclk <= (ampspi_chsel & 8'h04) ? ampspi_sclk : 1'b1;
    spi3_mosi <= (ampspi_chsel & 8'h04) ? ampspi_mosi : 1'b1;
    spi3_adc_vga_csn <= ((ampspi_chsel & 8'h04) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi3_dac_vga1_csn <= ((ampspi_chsel & 8'h04) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi3_dac_vga2_csn <= ((ampspi_chsel & 8'h04) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

    spi4_sclk <= (ampspi_chsel & 8'h08) ? ampspi_sclk : 1'b1;
    spi4_mosi <= (ampspi_chsel & 8'h08) ? ampspi_mosi : 1'b1;
    spi4_adc_vga_csn <= ((ampspi_chsel & 8'h08) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi4_dac_vga1_csn <= ((ampspi_chsel & 8'h08) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi4_dac_vga2_csn <= ((ampspi_chsel & 8'h08) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;
  
    spi5_sclk <= (ampspi_chsel & 8'h10) ? ampspi_sclk : 1'b1;
    spi5_mosi <= (ampspi_chsel & 8'h10) ? ampspi_mosi : 1'b1;
    spi5_adc_vga_csn <= ((ampspi_chsel & 8'h10) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi5_dac_vga1_csn <= ((ampspi_chsel & 8'h10) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi5_dac_vga2_csn <= ((ampspi_chsel & 8'h10) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;
  
    spi6_sclk <= (ampspi_chsel & 8'h20) ? ampspi_sclk : 1'b1;
    spi6_mosi <= (ampspi_chsel & 8'h20) ? ampspi_mosi : 1'b1;
    spi6_adc_vga_csn <= ((ampspi_chsel & 8'h20) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi6_dac_vga1_csn <= ((ampspi_chsel & 8'h20) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi6_dac_vga2_csn <= ((ampspi_chsel & 8'h20) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

    spi7_sclk <= (ampspi_chsel & 8'h40) ? ampspi_sclk : 1'b1;
    spi7_mosi <= (ampspi_chsel & 8'h40) ? ampspi_mosi : 1'b1;
    spi7_adc_vga_csn <= ((ampspi_chsel & 8'h40) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi7_dac_vga1_csn <= ((ampspi_chsel & 8'h40) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi7_dac_vga2_csn <= ((ampspi_chsel & 8'h40) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;

    spi8_sclk <= (ampspi_chsel & 8'h80) ? ampspi_sclk : 1'b1;
    spi8_mosi <= (ampspi_chsel & 8'h80) ? ampspi_mosi : 1'b1;
    spi8_adc_vga_csn <= ((ampspi_chsel & 8'h80) && (ampspi_chipsel & 3'h1)) ? ampspi_csn : 1'b1;
    spi8_dac_vga1_csn <= ((ampspi_chsel & 8'h80) && (ampspi_chipsel & 3'h2)) ? ampspi_csn : 1'b1;
    spi8_dac_vga2_csn <= ((ampspi_chsel & 8'h80) && (ampspi_chipsel & 3'h4)) ? ampspi_csn : 1'b1;
  end

  wire       wb_rst;
  wire       wb_cyc;
  wire       wb_stb;
  wire       wb_we;
  wire [7:0] wb_adr;
  wire [7:0] wb_dati;
  wire [7:0] wb_dato;

  wire spi_irq;

  spi_efb efb 
    (
     .wb_clk_i(osc_clk), 
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

	assign led0 = 0;
	assign led1 = 0;
	assign led2 = 0;
	assign led3 = 0;

/*
  wire [3:0] leds;
  wire [7:0] pwr_en;
  


  wire [7:0] address;
  wire       wr_en, rd_en;
  wire [7:0] wr_data;
  wire [7:0] rd_data;
  wire xfer_done;
  wire xfer_req;

  wire spi_irq;


  assign ampspi_miso = (ampspi_chsel & 8'h01) ? spi1_miso :
		       (ampspi_chsel & 8'h02) ? spi2_miso :
		       (ampspi_chsel & 8'h04) ? spi3_miso :
		       (ampspi_chsel & 8'h08) ? spi4_miso :
		       (ampspi_chsel & 8'h10) ? spi5_miso :
		       (ampspi_chsel & 8'h20) ? spi6_miso :
		       (ampspi_chsel & 8'h40) ? spi7_miso :
		       (ampspi_chsel & 8'h80) ? spi8_miso : 1'b1;
  
  
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
  
  

  // Internal Oscillator
  // defparam OSCH_inst.NOM_FREQ = "2.08"; // This is the default frequency defparam
  //OSCH_inst.NOM_FREQ = "100";  

  
  assign wb_clk = osc_clk;
  

  
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
	.wb_write_data(wr_data),
	.pwr_en(pwr_en),
	.leds(leds),
	.ampchan(ampspi_chsel),
	.ampcs(ampspi_chipsel)
	);
*/

endmodule
