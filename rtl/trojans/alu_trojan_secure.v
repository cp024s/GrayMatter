// =====================================================
// Trojan Wrapper
// Stable interface for testbench
// =====================================================

`timescale 1ns/1ps

module alu_trojan_secure (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [3:0]  A,
    input  wire [3:0]  B,
    input  wire [1:0]  op,
    output wire [3:0]  result,
    output wire        carry,
    output wire        zero,
    output wire        overflow
);

`ifdef TROJAN_V1
    alu_trojan_variant1 u_impl (
        .clk(clk), .rst_n(rst_n),
        .A(A), .B(B), .op(op),
        .result(result),
        .carry(carry),
        .zero(zero),
        .overflow(overflow)
    );

`elsif TROJAN_V2
    alu_trojan_variant2 u_impl (
        .clk(clk), .rst_n(rst_n),
        .A(A), .B(B), .op(op),
        .result(result),
        .carry(carry),
        .zero(zero),
        .overflow(overflow)
    );

`elsif TROJAN_V3
    alu_trojan_variant3 u_impl (
        .clk(clk), .rst_n(rst_n),
        .A(A), .B(B), .op(op),
        .result(result),
        .carry(carry),
        .zero(zero),
        .overflow(overflow)
    );

`else
    // Safety net: no Trojan selected
    initial begin
        $error("No TROJAN variant selected!");
        $stop;
    end
`endif

endmodule
