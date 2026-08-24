#!/bin/bash
# run_pipeline.sh
python src/preprocessing/clean_descriptions.py
python src/preprocessing/clean_games.py
python src/preprocessing/clean_steamspy.py
python src/preprocessing/clean_tags_genres_categories.py
python src/preprocessing/clean_reviews.py
python src/preprocessing/merge_datasets.py