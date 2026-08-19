def get_publisher_products(df, publisher):

    data = df[df["publisher"] == publisher]

    columns = [
        "app_id",
        "name",
        "genres",
        "tags",
        "categories",
        "about"
    ]

    return data[columns].to_dict("records")

# ===== Possible functions to implement =====
# get_game_descriptions()
# get_publisher_genres()
# get_publisher_tags()
# get_categories()
# get_portfolio_summary()
