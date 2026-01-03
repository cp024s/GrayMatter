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

`ifdef INCLUDE_TROJAN

    `ifdef TROJAN_V1
        alu_trojan_variant_1 impl (.*);
    `elsif TROJAN_V2
        alu_trojan_variant_2 impl (.*);
    `elsif TROJAN_V3
        alu_trojan_variant_3 impl (.*);
    `else
        // Safety fallback
        alu_clean_secure impl (.*);
    `endif

`else
    alu_clean_secure impl (.*);
`endif

endmodule
