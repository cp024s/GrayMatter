`timescale 1ns/1ps

module tb_alu_secure;

    // =========================================
    // Parameters
    // =========================================
    localparam int  NUM_CYCLES = 10000;   // >= 5k, research-safe
    localparam time CLK_PERIOD = 10ns;

    // =========================================
    // Clock / Reset
    // =========================================
    logic clk;
    logic rst_n;

    // =========================================
    // Shared Stimulus
    // =========================================
    logic [3:0] A;
    logic [3:0] B;
    logic [1:0] op;

    // =========================================
    // Outputs: CLEAN
    // =========================================
    logic [3:0] result_clean;
    logic       carry_clean;
    logic       zero_clean;
    logic       overflow_clean;

    // =========================================
    // Outputs: TROJAN
    // =========================================
    logic [3:0] result_trojan;
    logic       carry_trojan;
    logic       zero_trojan;
    logic       overflow_trojan;

    // =========================================
    // DUTs
    // =========================================
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

    // =========================================
    // Clock Generation
    // =========================================
    initial clk = 0;
    always #(CLK_PERIOD/2) clk = ~clk;

    // =========================================
    // Reset Sequence
    // =========================================
    initial begin
        rst_n = 0;
        A     = '0;
        B     = '0;
        op    = '0;

        repeat (5) @(posedge clk);
        rst_n = 1;
    end

    // =========================================
    // VCD Dumping (MANDATORY)
    // =========================================
    initial begin
        $dumpfile("alu_secure.vcd");
        $dumpvars(0, tb_alu_secure);
    end

    // =========================================
    // Random Stimulus Generator
    // (FSM-aligned, reproducible)
    // =========================================
    int unsigned seed;

    initial begin
        seed = 32'hC0FFEE42;
        wait (rst_n);

        for (int i = 0; i < NUM_CYCLES; i++) begin
            @(posedge clk);

            // Update inputs ONLY during IDLE
            if (u_clean.state == u_clean.IDLE) begin
                A  <= $urandom(seed) & 4'hF;
                B  <= $urandom(seed) & 4'hF;
                op <= $urandom(seed) & 2'h3;
            end
        end

        // Allow pipeline to drain
        repeat (10) @(posedge clk);

        $display("Simulation completed: %0d cycles", NUM_CYCLES);
        $finish;
    end

    // =========================================
    // Optional Functional Equivalence Check
    // (Valid outputs only, WB stage)
    // =========================================
`ifdef CHECK_EQUIVALENCE
    always @(posedge clk) begin
        if (rst_n && u_clean.state == u_clean.WB) begin
            if (result_clean   !== result_trojan   ||
                carry_clean    !== carry_trojan    ||
                zero_clean     !== zero_trojan     ||
                overflow_clean !== overflow_trojan) begin

                $error("FUNCTIONAL MISMATCH DETECTED");
                $error("CLEAN  : res=%h carry=%b zero=%b ovf=%b",
                       result_clean, carry_clean, zero_clean, overflow_clean);
                $error("TROJAN : res=%h carry=%b zero=%b ovf=%b",
                       result_trojan, carry_trojan, zero_trojan, overflow_trojan);
                $stop;
            end
        end
    end
`endif

endmodule
