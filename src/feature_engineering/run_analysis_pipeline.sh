#!/bin/bash
# run_pipeline.sh
python src/feature_engineering/build_publisher_features.py
python src/feature_engineering/build_publisher_scores.py
python src/feature_engineering/sensitivity_analysis_weights.py
