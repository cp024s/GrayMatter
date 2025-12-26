module alu_clean_secure (
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

    // =============================
    // FSM
    // =============================
    typedef enum logic [1:0] {
        IDLE = 2'b00,
        EXEC = 2'b01,
        WB   = 2'b10
    } state_t;

    state_t state, next_state;

    // =============================
    // Long-term temporal state
    // =============================
    reg [9:0] cycle_ctr;

    // =============================
    // Background switching noise
    // =============================
    reg [7:0] noise_reg_a;
    reg [7:0] noise_reg_b;

    // =============================
    // ALU internals
    // =============================
    reg [4:0] add_r, sub_r;
    reg [3:0] and_r, or_r;

    // =============================
    // FSM sequencing
    // =============================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    always @(*) begin
        case (state)
            IDLE: next_state = EXEC;
            EXEC: next_state = WB;
            WB:   next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end

    // =============================
    // Cycle counter
    // =============================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            cycle_ctr <= 10'd0;
        else
            cycle_ctr <= cycle_ctr + 1'b1;
    end

    // =============================
    // Background noise logic
    // =============================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            noise_reg_a <= 8'hA5;
            noise_reg_b <= 8'h3C;
        end else begin
            noise_reg_a <= {noise_reg_a[6:0], noise_reg_a[7]} ^ cycle_ctr[7:0];
            noise_reg_b <= noise_reg_b + noise_reg_a;
        end
    end

    // =============================
    // ALU combinational logic
    // =============================
    always @(*) begin
        add_r = {1'b0, A} + {1'b0, B};
        sub_r = {1'b0, A} - {1'b0, B};
        and_r = A & B;
        or_r  = A | B;
    end

    // =============================
    // Writeback (FIXED ZERO FLAG)
    // =============================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result   <= 4'd0;
            carry    <= 1'b0;
            zero     <= 1'b0;
            overflow <= 1'b0;
        end else if (state == WB) begin
            case (op)
                2'b00: begin
                    result   <= add_r[3:0];
                    carry    <= add_r[4];
                    overflow <= (A[3] == B[3]) && (A[3] != add_r[3]);
                end
                2'b01: begin
                    result   <= sub_r[3:0];
                    carry    <= sub_r[4];
                    overflow <= (A[3] != B[3]) && (A[3] != sub_r[3]);
                end
                2'b10: begin
                    result   <= and_r;
                    carry    <= 1'b0;
                    overflow <= 1'b0;
                end
                2'b11: begin
                    result   <= or_r;
                    carry    <= 1'b0;
                    overflow <= 1'b0;
                end
            endcase

            // Correct zero flag (no sequential bug)
            zero <= (
                (op == 2'b00 && add_r[3:0] == 4'b0) ||
                (op == 2'b01 && sub_r[3:0] == 4'b0) ||
                (op == 2'b10 && and_r       == 4'b0) ||
                (op == 2'b11 && or_r        == 4'b0)
            );
        end
    end

endmodule
