import pandas as pd

def get_publisher_stats(df, publisher):

    data = df[df["publisher"] == publisher]

    return {
        "publisher": publisher,
        "games": data["app_id"].nunique(),
        "total_reviews": int(data["total_reviews"].sum()),
        "avg_positive_ratio": data["positive_ratio"].mean(),
        "avg_price": data["price"].mean()
    }

# ===== Possible functions to implement =====
# get_all_publishers()
# get_publisher_stats()
# get_top_games()
# get_review_performance()
# get_sales_performance()
# get_release_history()
# get_genre_diversity()
# get_portfolio_concentration()