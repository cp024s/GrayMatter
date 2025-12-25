# ============================================================
# Hardware Trojan Detection — Modular Simulation Makefile
# Supports Vivado and Icarus via backend abstraction
# ============================================================

# ------------------------
# Tool selection
# ------------------------
SIM        ?= vivado          # Options: vivado | iverilog
PYTHON     := python3

# ------------------------
# Directories
# ------------------------
SIM_DIR    := sim
ANA_DIR    := analysis
ACT_DIR    := activity
RES_DIR    := results
CFG_DIR    := configs
EXP_DIR    := experiments

# ------------------------
# Config files
# ------------------------
SIM_CFG    := $(CFG_DIR)/sim_config.yaml
MC_CFG     := $(CFG_DIR)/mc_config.yaml
DET_CFG    := $(CFG_DIR)/detection_thresholds.yaml

# ------------------------
# Default target
# ------------------------
.DEFAULT_GOAL := help

# ------------------------
# Phony targets
# ------------------------
.PHONY: help \
        baseline detect \
        exp_clean_vs_clean exp_clean_vs_trojan \
        plots clean

# ============================================================
# Help
# ============================================================
help:
	@echo ""
	@echo "Hardware Trojan Detection — Modular Makefile"
	@echo "--------------------------------------------"
	@echo "Backend selection:"
	@echo "  make <target> SIM=iverilog"
	@echo "  make <target> SIM=vivado"
	@echo ""
	@echo "Core targets:"
	@echo "  make baseline             Build clean baseline distribution"
	@echo "  make detect               Run confidence-based detection"
	@echo ""
	@echo "Experiments:"
	@echo "  make exp_clean_vs_clean   False-alarm characterization"
	@echo "  make exp_clean_vs_trojan  Detection experiment"
	@echo ""
	@echo "Artifacts:"
	@echo "  make plots                Generate matplotlib plots"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                Remove generated artifacts"
	@echo ""

# ============================================================
# Baseline Modeling (Monte Carlo)
# ============================================================
baseline:
	$(PYTHON) $(ANA_DIR)/monte_carlo/mc_engine.py \
		--backend $(SIM) \
		--sim_cfg $(SIM_CFG) \
		--mc_cfg  $(MC_CFG)

# ============================================================
# Detection / Inference
# ============================================================
detect:
	$(PYTHON) $(ANA_DIR)/detector.py \
		--backend $(SIM) \
		--sim_cfg $(SIM_CFG) \
		--det_cfg $(DET_CFG)

# ============================================================
# Experiments
# ============================================================
exp_clean_vs_clean:
	$(PYTHON) $(EXP_DIR)/exp_clean_vs_clean/run.py --backend $(SIM)

exp_clean_vs_trojan:
	$(PYTHON) $(EXP_DIR)/exp_clean_vs_trojan/run.py --backend $(SIM)

# ============================================================
# Plot Generation
# ============================================================
plots:
	$(PYTHON) $(ANA_DIR)/plots/generate_plots.py

# ============================================================
# Cleanup
# ============================================================
clean:
	rm -rf $(ACT_DIR)/vcd/*
	rm -rf $(ACT_DIR)/saif/*
	rm -rf $(ACT_DIR)/parsed/*
	rm -rf $(RES_DIR)/plots/*
	rm -rf $(RES_DIR)/summaries/*
	rm -rf $(SIM_DIR)/logs/*

# --------------------------------------------------
# Python cache cleanup
# --------------------------------------------------

.PHONY: clean_pycache

clean_pycache:
	@echo "[CLEAN] Removing Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + || true
	@find . -type f -name "*.pyc" -delete || true
	@find . -type f -name "*.pyo" -delete || true
	@echo "[OK] Python cache cleaned."

# --------------------------------------------------
# Standalone report generation (mock data)
# --------------------------------------------------

.PHONY: run_report_only

run_report_only:
	@echo "[RUN] Generating unified analysis report (standalone)..."
	@python -m scripts.run_report_only
	@echo "[OK] Report generated in results/plots/"
