module alu_trojan_variant0 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [3:0]  A,
    input  wire [3:0]  B,
    input  wire [1:0]  op,
    output reg  [3:0]  result,
    output reg         carry,
    output reg         zero,
    output reg         overflow
);

    // IDENTICAL to clean design (no trojan logic)
    alu_clean_secure u_clean_clone (
        .clk(clk),
        .rst_n(rst_n),
        .A(A),
        .B(B),
        .op(op),
        .result(result),
        .carry(carry),
        .zero(zero),
        .overflow(overflow)
    );

endmodule
