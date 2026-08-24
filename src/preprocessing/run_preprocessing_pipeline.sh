#!/bin/bash
# run_pipeline.sh
python clean_descriptions.py
python clean_games.py
python clean_steamspy.py
python clean_tags_genres_categories.py
python clean_reviews.py
python merge_datasets.py