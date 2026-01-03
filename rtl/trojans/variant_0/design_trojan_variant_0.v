module alu_trojan_variant_0 (
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

    // -------------------------------------------------
    // Loud always-on Trojan payload (positive control)
    // -------------------------------------------------
    reg [15:0] trojan_counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            trojan_counter <= 16'd0;
        else
            trojan_counter <= trojan_counter + 1'b1;
    end

    // -------------------------------------------------
    // Clean ALU logic (unchanged)
    // -------------------------------------------------
    alu_clean_secure u_clean (
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
