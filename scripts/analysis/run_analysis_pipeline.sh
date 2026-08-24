#!/bin/bash
# run_pipeline.sh
python scripts/analysis/build_publisher_features.py
python scripts/analysis/build_publisher_scores.py
python scripts/analysis/sensitivity_analysis_weights.py
