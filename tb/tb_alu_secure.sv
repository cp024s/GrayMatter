`timescale 1ns/1ps

module tb_alu_secure;

    // ===============================
    // Parameters
    // ===============================
    localparam int  NUM_CYCLES = 10000;
    localparam time CLK_PERIOD = 10ns;

    // ===============================
    // Clock / Reset
    // ===============================
    logic clk;
    logic rst_n;

    // ===============================
    // Shared Stimulus
    // ===============================
    logic [3:0] A;
    logic [3:0] B;
    logic [1:0] op;

    // ===============================
    // CLEAN outputs
    // ===============================
    logic [3:0] result_clean;
    logic       carry_clean;
    logic       zero_clean;
    logic       overflow_clean;

    // ===============================
    // TROJAN outputs
    // ===============================
    logic [3:0] result_trojan;
    logic       carry_trojan;
    logic       zero_trojan;
    logic       overflow_trojan;

    // ===============================
    // CLEAN DUT (ALWAYS PRESENT)
    // ===============================
    alu_clean_secure u_clean (
        .clk      (clk),
        .rst_n    (rst_n),
        .A        (A),
        .B        (B),
        .op       (op),
        .result   (result_clean),
        .carry    (carry_clean),
        .zero     (zero_clean),
        .overflow (overflow_clean)
    );

    // ===============================
    // TROJAN DUT (ONLY WHEN ENABLED)
    // ===============================
`ifdef INCLUDE_TROJAN
    alu_trojan_secure u_trojan (
        .clk      (clk),
        .rst_n    (rst_n),
        .A        (A),
        .B        (B),
        .op       (op),
        .result   (result_trojan),
        .carry    (carry_trojan),
        .zero     (zero_trojan),
        .overflow (overflow_trojan)
    );
`else
    // Dummy values so analysis code never breaks
    assign result_trojan   = 4'b0;
    assign carry_trojan    = 1'b0;
    assign zero_trojan     = 1'b0;
    assign overflow_trojan = 1'b0;
`endif

    // ===============================
    // Clock
    // ===============================
    initial clk = 0;
    always #(CLK_PERIOD/2) clk = ~clk;

    // ===============================
    // Reset
    // ===============================
    initial begin
        rst_n = 0;
        A = 0; B = 0; op = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;
    end

    // ===============================
    // VCD
    // ===============================
    initial begin
        $dumpfile("alu_secure.vcd");
        $dumpvars(0, tb_alu_secure);
    end

    // ===============================
    // Stimulus
    // ===============================
    int unsigned seed;

    initial begin
        seed = 32'hC0FFEE;
        wait (rst_n);

        for (int i = 0; i < NUM_CYCLES; i++) begin
            @(posedge clk);
            if (u_clean.state == u_clean.IDLE) begin
                A  <= $urandom(seed) & 4'hF;
                B  <= $urandom(seed) & 4'hF;
                op <= $urandom(seed) & 2'h3;
            end
        end

        repeat (10) @(posedge clk);
        $display("Simulation completed: %0d cycles", NUM_CYCLES);
        $finish;
    end

endmodule
