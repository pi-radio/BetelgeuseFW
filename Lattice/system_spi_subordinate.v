`define SPITXDR 8'h59
`define SPIISR   8'h5A
`define SPIRXDR 8'h5B
  
`define STATE_IDLE         0
`define STATE_READ_RX      1
`define STATE_WRITE_DUMMY  2
`define STATE_WAIT_CMD     3
`define STATE_LOAD_CMD     4
`define STATE_SENSE_RDY    5
`define STATE_WAIT_RDY     6
`define STATE_WAIT_DATA_TX 7
`define STATE_WAIT_DATA_RX 8

`define REG_PWR_EN         0
`define REG_LEDS           1
`define REG_AMPCHAN        2
`define REG_AMPCS          3

module system_spi_subordinate
  (
   input  wire clk,
   input  wire rstn,
   input  wire spi_csn,
   output reg rd_en,
   output reg wr_en,
   output reg [7:0] address,
   input wire wb_xfer_done,
   input wire wb_xfer_rdy,
   input wire spi_irq,
   input wire [7:0] wb_read_data,
   output reg [7:0] wb_write_data,
   output wire [7:0] pwr_en,
   output wire [3:0] leds,
   output wire [7:0] ampchan,
   output wire [2:0] ampcs
   );

  reg [2:0] csn_buf;

  always @(posedge clk or negedge rstn) csn_buf = (rstn == 0) ? 3'b111 : { csn_buf[1:0], spi_csn };
  
  wire spi_cmd_start_edge = csn_buf[2] & ~csn_buf[1];
  wire spi_cmd_end_edge = ~csn_buf[2] & csn_buf[1];

  reg spi_cmd_start_r;
 

  reg [7:0] spi_regs[0:2];

  reg [2:0] reg_addr;
  reg reg_rw;
  
  reg [7:0] spi_cmd;
  
  assign pwr_en = spi_regs[`REG_PWR_EN];
  assign leds = spi_regs[`REG_LEDS][3:0];
  assign ampchan = spi_regs[`REG_AMPCHAN];
  assign ampcs = spi_regs[`REG_AMPCS][2:0];
  
  reg [3:0] state;
  reg [3:0] cmpl_state;

  always @(posedge clk or negedge rstn) begin
    spi_cmd_start_r <= spi_cmd_start_edge ? 1'b1 : (~rstn || state == `STATE_IDLE || state == `STATE_READ_RX) ? 1'b0 : spi_cmd_start_r;
  end

  reg spi_end_txn;

  always @(posedge clk or negedge rstn) begin
    spi_end_txn <= (~rstn || state == `STATE_IDLE) ? 1'b0 : 1'b1;
  end
  
  wire spi_cmd_start = spi_cmd_start_edge | spi_cmd_start_r;
  wire spi_cmd_done = spi_cmd_end_edge | spi_end_txn;
  wire spi_rx_rdy = rstn & wb_read_data[3];
  wire spi_tx_rdy = rstn & wb_read_data[4];

  integer i;
  
  always @(posedge clk)
    begin
      if (~rstn) begin
	state <= `STATE_IDLE;
	rd_en <= 1'b0;
	wr_en <= 1'b0;
	address <= `SPITXDR;
	wb_write_data <= 8'b0;
	reg_addr <= 3'b0;

	spi_regs[`REG_PWR_EN] = 8'hFF;
	spi_regs[`REG_LEDS] = 8'b0;
	spi_regs[`REG_AMPCHAN] = 8'b0;
	spi_regs[`REG_AMPCS] = 8'b0;
	spi_regs[4] = 8'b0;
	spi_regs[5] = 8'b0;
	spi_regs[6] = 8'b0;
	spi_regs[7] = 8'b0;
	
      end else begin
	rd_en <= 1'b0;
	wr_en <= 1'b0;
	address <= `SPITXDR;
	wb_write_data <= 8'b0;
	
	case (state)
	  `STATE_IDLE: begin
	    if (spi_cmd_start && wb_xfer_rdy) begin
	      state <= `STATE_READ_RX;
	      rd_en <= 1'b1;
	      address <= `SPIRXDR;
	    end
	  end
	  
	  `STATE_READ_RX: begin
	    if (wb_xfer_done) begin
	      state <= `STATE_WRITE_DUMMY;
	      wr_en <= 1'b1;
	      wb_write_data <= 8'b0;
	      address <= `SPITXDR;
	    end
	  end

	  `STATE_WRITE_DUMMY: begin
	    if (wb_xfer_done) begin
	      state <= `STATE_WAIT_CMD;
	      rd_en <= 1'b1;
	      address <= `SPIISR;
	    end
	  end

	  `STATE_WAIT_CMD: begin
	    if (wb_xfer_done && spi_rx_rdy) begin
	      state <= `STATE_LOAD_CMD;
	      rd_en <= 1'b1;
	      address <= `SPIRXDR;
	    end else if (wb_xfer_done && spi_cmd_done) begin
	      state <= `STATE_IDLE;
	    end else if (wb_xfer_done && spi_tx_rdy) begin
	      state <= `STATE_WRITE_DUMMY;
	      wr_en <= 1'b1;
	      wb_write_data <= 8'b0;
	      address <= `SPITXDR;	      
	    end else if (wb_xfer_done) begin
	      rd_en <= 1'b1;
	      address <= `SPIISR;
	    end
	  end // case: `STATE_WAIT_CMD

	  // latch the register no
	  `STATE_LOAD_CMD: begin
	    if (wb_xfer_done) begin
	      address <= `SPITXDR;
	      wr_en <= 1'b1;

	      reg_rw <= wb_read_data[7];
	      reg_addr <= wb_read_data[2:0];
	      wb_write_data <= spi_regs[wb_read_data[2:0]];	      
	      state <= `STATE_SENSE_RDY;		
	    end
	  end  // case: `STATE_LOAD_CMD
	  
	  `STATE_SENSE_RDY: begin
	    if (spi_cmd_done) begin
	      state <= `STATE_IDLE;
	    end else if (wb_xfer_done) begin
	      rd_en <= 1'b1;
	      address <= `SPIISR;
	      state <= `STATE_WAIT_RDY;
	    end
	  end

	  `STATE_WAIT_RDY: begin
	    if (spi_cmd_done) begin
	      state <= `STATE_IDLE;
	    end else if (wb_xfer_done && spi_tx_rdy) begin
		wr_en <= 1'b1;
		address <= `SPITXDR;
		wb_write_data <= spi_regs[reg_addr+1];
		state <= `STATE_WAIT_DATA_TX;
	    end else if (wb_xfer_done && spi_rx_rdy) begin
		rd_en <= 1'b1;
		address <= `SPIRXDR;
		state <= `STATE_WAIT_DATA_RX;
	    end else if (wb_xfer_done && spi_cmd_done) begin
	      state <= `STATE_IDLE;
	    end else begin
	      rd_en <= 1'b0;
	      address <= `SPIISR;
	      state <= `STATE_WAIT_RDY;
	    end // else: !if(wb_xfer_done & spi_rx_rdy)	    
	  end // case: `STATE_WAIT_RDY

	  `STATE_WAIT_DATA_TX: begin
	    if (wb_xfer_done) begin
	      rd_en <= 1'b1;
	      address <= `SPIISR;
	      state <= `STATE_WAIT_RDY;
	    end else begin
	      wr_en <= 1'b1;
	      address <= `SPITXDR;
	      wb_write_data <= spi_regs[reg_addr+1];
	      state <= `STATE_WAIT_DATA_TX;
	    end
	  end

	  `STATE_WAIT_DATA_RX: begin
	    if (wb_xfer_done) begin
	      spi_regs[reg_addr] <= wb_read_data;
	      reg_addr <= reg_addr + 1;
	      rd_en <= 1'b1;
	      address <= `SPIISR;
	      state <= `STATE_WAIT_RDY;
	    end else begin
	      rd_en <= 1'b1;
	      address <= `SPIRXDR;
	      state <= `STATE_WAIT_DATA_RX;
	    end
	  end
	endcase
      end
    end
endmodule
