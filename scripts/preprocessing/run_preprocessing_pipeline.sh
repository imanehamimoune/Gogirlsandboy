#!/bin/bash
# run_pipeline.sh
python scripts/preprocessing/clean_games.py
python scripts/preprocessing/clean_steamspy.py
python scripts/preprocessing/clean_tags_genres_categories.py
python scripts/preprocessing/clean_reviews.py
python scripts/preprocessing/merge_datasets.py