#!/bin/bash
# Live Experiment Execution Script
# Orchestrates the full experiment pipeline for live mode.
#
# Usage:
#   ./run_live.sh                   # Run all experiments
#   ./run_live.sh --check-only      # Only run prerequisite checks
#   ./run_live.sh --experiment 1    # Run specific experiment
#   ./run_live.sh --with-judge      # Run with LLM judge mode
#
# Prerequisites:
#   - Neo4j running with populated KG (>= 500 entities)
#   - ANTHROPIC_API_KEY set in environment
#   - Python venv at /home/guhaase/projetos/panelbox/graphrag/.venv/

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON="/home/guhaase/projetos/panelbox/graphrag/.venv/bin/python"
RESULTS_DIR="${BASE_DIR}/results/live"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${RESULTS_DIR}/run_${TIMESTAMP}.log"

# Default options
CHECK_ONLY=false
EXPERIMENT="all"
WITH_JUDGE=false
MAX_QUESTIONS=0
SEED=42

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --experiment)
            EXPERIMENT="$2"
            shift 2
            ;;
        --with-judge)
            WITH_JUDGE=true
            shift
            ;;
        --max-questions)
            MAX_QUESTIONS="$2"
            shift 2
            ;;
        --seed)
            SEED="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--check-only] [--experiment N] [--with-judge] [--max-questions N] [--seed N]"
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$RESULTS_DIR"

echo "========================================================================"
echo "  GraphRAG Live Experiment Runner"
echo "  Timestamp: $TIMESTAMP"
echo "  Results: $RESULTS_DIR"
echo "  Log: $LOG_FILE"
echo "========================================================================"
echo ""

# Step 1: Check prerequisites
echo "[1/6] Checking prerequisites..."
if $PYTHON "$SCRIPT_DIR/check_prerequisites.py" 2>&1 | tee -a "$LOG_FILE"; then
    echo "  All prerequisites passed."
else
    echo "  WARNING: Some prerequisites failed."
    echo "  Live experiments may not work correctly."
    echo ""
    if $CHECK_ONLY; then
        exit 1
    fi
    read -p "  Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if $CHECK_ONLY; then
    echo "Check-only mode. Exiting."
    exit 0
fi

echo ""

# Build common arguments
COMMON_ARGS="--seed $SEED --results-dir $RESULTS_DIR"
if [ "$MAX_QUESTIONS" -gt 0 ]; then
    COMMON_ARGS="$COMMON_ARGS --max-questions $MAX_QUESTIONS"
fi

JUDGE_ARG=""
if $WITH_JUDGE; then
    JUDGE_ARG="--judge-mode llm"
fi

# Step 2: Run experiments
if [ "$EXPERIMENT" = "all" ]; then
    echo "[2/6] Running Experiment 1: Hallucination Evaluation..."
    $PYTHON "$SCRIPT_DIR/run_experiments.py" --experiment 1 $COMMON_ARGS $JUDGE_ARG 2>&1 | tee -a "$LOG_FILE"
    echo ""

    echo "[3/6] Running Experiment 2: Token Economy..."
    $PYTHON "$SCRIPT_DIR/run_experiments.py" --experiment 2 $COMMON_ARGS 2>&1 | tee -a "$LOG_FILE"
    echo ""

    echo "[4/6] Running Experiment 3: Speed Benchmarks..."
    $PYTHON "$SCRIPT_DIR/run_experiments.py" --experiment 3 $COMMON_ARGS 2>&1 | tee -a "$LOG_FILE"
    echo ""

    echo "[5/6] Running Experiment 5: Full Benchmark..."
    $PYTHON "$SCRIPT_DIR/run_experiments.py" --experiment 5 $COMMON_ARGS 2>&1 | tee -a "$LOG_FILE"
    echo ""

    echo "[6/6] Running Experiment 6: Ablation Study..."
    $PYTHON "$SCRIPT_DIR/run_experiments.py" --experiment 6 $COMMON_ARGS 2>&1 | tee -a "$LOG_FILE"
    echo ""
else
    echo "[2/2] Running Experiment $EXPERIMENT..."
    $PYTHON "$SCRIPT_DIR/run_experiments.py" --experiment "$EXPERIMENT" $COMMON_ARGS $JUDGE_ARG 2>&1 | tee -a "$LOG_FILE"
    echo ""
fi

# Step 3: Generate summary
echo "========================================================================"
echo "  Experiment Run Complete"
echo "  Results saved to: $RESULTS_DIR"
echo "  Log file: $LOG_FILE"
echo ""
echo "  Output files:"
ls -la "$RESULTS_DIR"/*.json 2>/dev/null || echo "  (no JSON files found)"
echo "========================================================================"

# Collect metadata
$PYTHON -c "
import json, platform, os
from datetime import datetime, timezone
metadata = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'hostname': platform.node(),
    'python_version': platform.python_version(),
    'os': platform.platform(),
    'experiment': '$EXPERIMENT',
    'seed': $SEED,
    'max_questions': $MAX_QUESTIONS,
    'judge_mode': 'llm' if '$WITH_JUDGE' == 'true' else 'heuristic',
    'results_dir': '$RESULTS_DIR',
}
with open('$RESULTS_DIR/metadata_${TIMESTAMP}.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print('Metadata saved.')
" 2>&1 | tee -a "$LOG_FILE"
