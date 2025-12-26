module alu_trojan_secure (
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

    // This is a CLEAN STUB.
    // Behavior is IDENTICAL to alu_clean_secure.
    // Purpose: baseline equivalence for experiment framework.

    // Include the clean logic directly
    // (copy-paste from alu_clean_secure)

    // FSM
    typedef enum logic [1:0] { IDLE, EXEC, WB } state_t;
    state_t state, next_state;

    reg [9:0] cycle_ctr;
    reg [7:0] noise_reg_a, noise_reg_b;
    reg [4:0] add_r, sub_r;
    reg [3:0] and_r, or_r;

    always @(posedge clk or negedge rst_n)
        if (!rst_n) state <= IDLE;
        else state <= next_state;

    always @(*) begin
        case (state)
            IDLE: next_state = EXEC;
            EXEC: next_state = WB;
            WB:   next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end

    always @(posedge clk or negedge rst_n)
        if (!rst_n) cycle_ctr <= 10'd0;
        else cycle_ctr <= cycle_ctr + 1'b1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            noise_reg_a <= 8'hA5;
            noise_reg_b <= 8'h3C;
        end else begin
            noise_reg_a <= {noise_reg_a[6:0], noise_reg_a[7]} ^ cycle_ctr[7:0];
            noise_reg_b <= noise_reg_b + noise_reg_a;
        end
    end

    always @(*) begin
        add_r = {1'b0, A} + {1'b0, B};
        sub_r = {1'b0, A} - {1'b0, B};
        and_r = A & B;
        or_r  = A | B;
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result <= 0;
            carry <= 0;
            zero <= 0;
            overflow <= 0;
        end else if (state == WB) begin
            case (op)
                2'b00: begin result <= add_r[3:0]; carry <= add_r[4]; end
                2'b01: begin result <= sub_r[3:0]; carry <= sub_r[4]; end
                2'b10: begin result <= and_r; carry <= 0; end
                2'b11: begin result <= or_r;  carry <= 0; end
            endcase
            zero <= (result == 0);
            overflow <= 0;
        end
    end

endmodule
