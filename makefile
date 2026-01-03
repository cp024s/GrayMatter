# ============================================================
# Hardware Trojan Detection — Unified Research + Pipeline Makefile
# ============================================================

# make help                → show commands
# make all                 → FULL PIPELINE (what you demo)
# make sim                 → run all simulations
# make analysis             → run all analysis
# make baseline             → Monte-Carlo baseline (research)
# make detect               → statistical detector only
# make exp_clean_vs_trojan  → paper experiment
# make plots                → figures
# make clean / wipe         → cleanup

# ------------------------
# Tool selection
# ------------------------
SIM        ?= iverilog          # vivado | iverilog
PYTHON     := PYTHONPATH=. python3

# ------------------------
# Directories
# ------------------------
ROOT       := .
SIM_DIR    := sim
ANA_DIR    := analysis
ACT_DIR    := activity
RES_DIR    := results
CFG_DIR    := configs
EXP_DIR    := experiments
SCR_DIR    := scripts

# ------------------------
# Config files (research path)
# ------------------------
SIM_CFG    := $(CFG_DIR)/sim_config.yaml
MC_CFG     := $(CFG_DIR)/mc_config.yaml
DET_CFG    := $(CFG_DIR)/detection_thresholds.yaml

# ------------------------
# Experiment params (pipeline path)
# ------------------------
CLEAN_SEEDS := 1 2 3 4 5 6 7 8 9 10
TROJAN_VARIANTS := v0 v1 v2

# ------------------------
# Default target
# ------------------------
.DEFAULT_GOAL := help

# ------------------------
# Phony targets
# ------------------------
.PHONY: help all sim analysis \
        clean-sim trojan-sim \
        analysis-clean analysis-trojan \
        baseline detect \
        exp_clean_vs_clean exp_clean_vs_trojan \
        plots clean wipe clean_pycache

# ============================================================
# HELP
# ============================================================
help:
	@echo ""
	@echo "Hardware Trojan Detection — Unified Makefile"
	@echo "--------------------------------------------"
	@echo ""
	@echo "Backend selection:"
	@echo "  make <target> SIM=iverilog"
	@echo "  make <target> SIM=vivado"
	@echo ""
	@echo "FULL PIPELINE:"
	@echo "  make all                  Run everything (demo-ready)"
	@echo ""
	@echo "PIPELINE STAGES:"
	@echo "  make sim                  All simulations"
	@echo "  make analysis             All analyses + reports"
	@echo ""
	@echo "RESEARCH TARGETS:"
	@echo "  make baseline             Monte-Carlo baseline"
	@echo "  make detect               Statistical detector"
	@echo ""
	@echo "EXPERIMENTS:"
	@echo "  make exp_clean_vs_clean"
	@echo "  make exp_clean_vs_trojan"
	@echo ""
	@echo "ARTIFACTS:"
	@echo "  make plots"
	@echo ""
	@echo "MAINTENANCE:"
	@echo "  make clean | make wipe"
	@echo ""

# ============================================================
# FULL PIPELINE (ONE COMMAND)
# ============================================================
all: sim analysis plots
	@echo "=============================================="
	@echo "✔ FULL HARDWARE TROJAN PIPELINE COMPLETE"
	@echo "Results available in ./results/"
	@echo "=============================================="

# ============================================================
# SIMULATIONS
# ============================================================
sim: clean-sim trojan-sim

clean-sim:
	@echo "▶ Running CLEAN simulations (multi-seed)"
	@for s in $(CLEAN_SEEDS); do \
		echo "  • clean seed $$s"; \
		$(PYTHON) $(EXP_DIR)/run_experiment.py --variant clean --seed $$s ; \
	done

trojan-sim:
	@echo "▶ Running TROJAN simulations"
	@for v in $(TROJAN_VARIANTS); do \
		echo "  • $$v"; \
		$(PYTHON) $(EXP_DIR)/run_experiment.py --variant $$v ; \
	done

# ============================================================
# ANALYSIS
# ============================================================
analysis: analysis-clean analysis-trojan

analysis-clean:
	@echo "▶ Analyzing CLEAN baseline"
	@for s in $(CLEAN_SEEDS); do \
		$(PYTHON) $(SCR_DIR)/run_analysis_from_vcd.py \
			--variant clean \
			--vcd $(RES_DIR)/clean/seed_$$s/alu_secure.vcd ; \
	done

analysis-trojan:
	@echo "▶ Analyzing TROJAN variants"
	@for v in $(TROJAN_VARIANTS); do \
		$(PYTHON) $(SCR_DIR)/run_analysis_from_vcd.py \
			--variant $$v \
			--vcd $(RES_DIR)/$$v/alu_secure.vcd ; \
	done

# ============================================================
# RESEARCH PATH (UNCHANGED, BUT CLEAN)
# ============================================================
baseline:
	$(PYTHON) $(ANA_DIR)/monte_carlo/mc_engine.py \
		--backend $(SIM) \
		--sim_cfg $(SIM_CFG) \
		--mc_cfg  $(MC_CFG)

detect:
	$(PYTHON) $(ANA_DIR)/detector.py \
		--backend $(SIM) \
		--sim_cfg $(SIM_CFG) \
		--det_cfg $(DET_CFG)

# ============================================================
# EXPERIMENTS (PAPER-ORIENTED)
# ============================================================
exp_clean_vs_clean:
	$(PYTHON) $(EXP_DIR)/exp_clean_vs_clean/run.py --backend $(SIM)

exp_clean_vs_trojan:
	$(PYTHON) $(EXP_DIR)/exp_clean_vs_trojan/run.py --backend $(SIM)

# ============================================================
# PLOTS
# ============================================================
plots:
	$(PYTHON) $(ANA_DIR)/plots/generate_plots.py || true

# ============================================================
# CLEANUP
# ============================================================
clean:
	rm -rf $(ACT_DIR)/vcd/*
	rm -rf $(ACT_DIR)/saif/*
	rm -rf $(ACT_DIR)/parsed/*
	rm -rf $(RES_DIR)/plots/*
	rm -rf $(RES_DIR)/summaries/*
	rm -rf $(SIM_DIR)/logs/*
	rm -rf simv
	@echo "[OK] Cleaned generated artifacts"

wipe: clean clean_pycache
	rm -rf $(RES_DIR)/*
	@echo "[OK] Full wipe complete"

clean_pycache:
	@echo "[CLEAN] Removing Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + || true
	@find . -type f -name "*.pyc" -delete || true
	@find . -type f -name "*.pyo" -delete || true
	@echo "[OK] Python cache cleaned"
