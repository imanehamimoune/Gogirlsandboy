# Data Preprocessing

The raw Steam data consisted of several separate datasets containing information on games, publishers, reviews, ownership estimates, genres, tags, categories, descriptions, and promotional material. Before the datasets were merged for analysis, each source was assessed and cleaned separately. 

## `games.csv`

The `games.csv` dataset contained the game-level information.

The file was loaded using backslash escaping to handle the source formatting. The `price_overview` variable contained JSON-formatted information. Therefore, the field parsed and expanded into separate `price_*` columns, while the original nested `price_overview` column was removed from the processed version.

Release dates were standardized by replacing the `"N"` placeholder with a missing value and converting values to a datetime format. The `is_free` variable was converted to Boolean format.

The `languages` field contained HTML and additional formatting information. A separate `full_audio_support` indicator was first extracted from this information. HTML tags, formatting markers, unnecessary whitespace, and the `"N"` placeholder were subsequently removed or standardized in the language field.

Several additional analytical variables were derived from the existing information. These included indicators for whether a game had a recurring subscription and whether it was discounted, as well as a count of the number of supported languages.

Two specifically identified game records were removed from the dataset based on their game names. Apart from these explicit exclusions, the preprocessing did not automatically remove unusual observations.

## `reviews.csv`

The reviews dataset required special parsing because the review text contained backslash-escaped quotation marks that interfered with standard CSV parsing. The file was therefore loaded with an explicit escape character and the Python parsing engine.

Placeholder null values originating from `\N` were normalized by converting the numeric-like variables using numeric coercion. This produced missing values where source values could not be interpreted numerically.

For the `review_score` variable, Steam uses a score of `0` when there are insufficient reviews to assign a review score. These zero values were therefore treated as meaningful information. Five observations in which `review_score` itself was unparseable were removed because the key review metric was unavailable.

Redundancy was checked before columns were removed. The relationship between `review_score` and `review_score_description` was verified, and `total` was confirmed to equal `positive + negative`. Consequently, `review_score_description` and `total` were removed. `steamspy_score_rank` was also removed because more than 99.9% of its observations were missing.

The SteamSpy positive and negative review counts were **not** removed. They disagreed with the official review counts in approximately 18% of observations and were therefore treated as estimates from a separate source.

Numeric variables were converted to appropriate integer or floating-point representations while retaining missing values where necessary. Review text was cleaned by decoding HTML entities, removing HTML tags, normalizing whitespace.

Duplicate records were removed, and the resulting data was validated to ensure that duplicate `app_id`s and complete duplicate rows were no longer present.

### AI-assisted preprocessing

Claude was used during the preprocessing of `reviews.csv`. A detailed prompt specified the required data-quality checks, cleaning rules, constraints, and validation requirements. The generated code was then used for the preprocessing procedure described above. Claude assisted in generating the preprocessing code based on the supplied requirements.

## `steamspy.csv`

During import, `app_id` was explicitly treated as an integer, while empty strings and `"N"` values were interpreted as missing values. Backslash escaping in the source export was also handled.

Duplicate `app_id` records were identified and removed by retaining the first occurrence, after which the data was ordered by `app_id`.

Developer and publisher names were standardized for analytical grouping. Excess whitespace was removed, primary companies were extracted where fields contained multiple companies, and separate normalized company keys were generated. Legal-form suffixes and selected descriptive suffixes were removed from these grouping keys. The original company fields were retained for display purposes. The normalized developer and publisher keys were also compared to create a `self_published` indicator.

SteamSpy ownership ranges such as `"20,000 .. 50,000"` were transformed into numeric lower and upper bounds and an ownership midpoint. A logarithmic version of the midpoint and an ordered ownership-bucket variable were also generated.

Price and initial-price values were converted from cents to euros. Additional variables identified free games and calculated implied discount percentages. Observations where the current price exceeded the initial price were flagged as inconsistent rather than removed. Initial prices above €200 were similarly flagged as potential price outliers and retained.

Concurrent-user counts were converted to numeric values, with negative counts treated as missing. Four playtime variables were found to contain only zero values throughout the export and were therefore removed because they carried no analytical information.

Counts of languages and genres were generated from the corresponding SteamSpy text fields. A proxy for estimated revenue was also calculated as the ownership midpoint multiplied by the current price. This measure was explicitly treated as an approximation rather than actual revenue because the underlying ownership estimates are bucketed and do not account for factors such as regional pricing, refunds, bundles, free-to-play behavior, or Steam's revenue share.

Finally, an `is_investable` indicator identified records with available publisher, price, and ownership information. Apart from duplicate identifiers and zero-information columns, questionable observations were generally flagged rather than automatically removed.

## `tags.csv`

The tags dataset was inspected for its structure, data types, missing values, duplicate rows, leading and trailing whitespace, empty strings, and inconsistent capitalization.

Because an individual game can legitimately have multiple tags, multiple observations for the same `app_id` were intentionally preserved. Only duplicate combinations of `app_id` and tag were considered redundant.

Tag values were stripped of leading and trailing whitespace, and the cleaning procedure included removal of empty tags and duplicate `app_id`–tag combinations where present. The original Steam naming conventions were deliberately retained instead of introducing unnecessary renaming or broader category consolidation.

The quality assessment ultimately found no material data-quality problems requiring observations to be removed.
The processed dataset was exported separately as `tags_cleaned.csv`.

## `genres.csv`

The genres dataset was similarly assessed for missing values, duplicates, whitespace, empty values, capitalization inconsistencies, and variation in categorical labels.

The principal issue was that equivalent genres appeared under different languages and naming conventions. A mapping dictionary was therefore used to standardize multilingual labels into consistent English categories. For example, different language variants referring to Action, Adventure, Casual, Indie, RPG, Simulation, Sports, and Strategy were mapped to common English labels.

Multiple genres for an individual game were intentionally retained because they represent valid many-to-many relationships. Following standardization, however, different source labels could map to the same English genre for the same game. Duplicate `app_id`–genre combinations created through this process were therefore removed.

The standardization reduced **121 original genre labels to 33 consistent English genre categories**. According to the preprocessing validation, no missing values or duplicate `app_id`–genre combinations remained after cleaning.

The resulting data was exported as `genres_cleaned.csv`.

## `categories.csv`

The categories dataset contained a similar multilingual standardization problem. Initial checks covered missing values, duplicates, whitespace, empty values, case inconsistencies, and the range of unique categories.

Two rounds of mapping were used to consolidate equivalent multilingual labels into standardized English categories. Importantly, standardization was based on functional equivalence rather than simply grouping similar concepts. Categories representing genuinely different Steam features were kept separate. For example, `PvP`, `Online PvP`, and `Shared/Split Screen PvP` remained distinct, as did the corresponding Co-op categories and different forms of VR functionality.

The process reduced **315 original category labels to 42 standardized English categories**. Because several original labels could map to the same standardized category for a game, the mapping process generated redundant `app_id`–category combinations. These duplicates were removed after standardization, resulting in the removal of **79 redundant rows**.
The cleaned dataset was exported as `categories_cleaned.csv`.

## `descriptions.csv`

The descriptions dataset contained the text fields `summary`, `extensive`, and `about`. A data-quality procedure was designed to inspect the dataset's shape, data types, missing values, duplicate rows and `app_id`s, empty text fields, remaining HTML, description lengths, and very short descriptions.

HTML was removed from each of the three description fields using BeautifulSoup while preserving the underlying textual content. Following HTML removal, records with fewer than 20 characters in any of the specified description fields were filtered from the processed version.

However, the descriptions dataset was ultimately **excluded from the merged master dataset**. The information relevant to the analytical objective was already represented through more standardized variables in the genres, tags, and categories datasets. These structured categorical variables were preferred over free-form descriptions for the subsequent publisher analysis. The exclusion of `descriptions.csv` was therefore primarily a feature-selection decision for the master dataset rather than simply a data-quality decision.

## `promotional.csv`

The promotional dataset was **excluded from the master dataset without being used as an analytical input**. It consists primarily of promotional and marketing-related information, including links to marketing images.

These variables were considered outside the scope of the analysis. The objective of the project is to identify and evaluate **high-performing publishers**, and the promotional fields did not provide relevant measures for evaluating publisher performance within the chosen analytical strategy.

The exclusion of `promotional.csv` should therefore be understood as a **relevance-based feature-selection decision**, rather than the result of poor data quality.

## Overall Preprocessing Approach

Across the datasets, preprocessing followed a conservative approach. Information was standardized where inconsistent formatting or multilingual labels would otherwise prevent meaningful comparison. Redundant variables were removed only when their redundancy was established, while variables representing similar information from genuinely different sources were retained. Missing values were generally preserved rather than imputed, and unusual or extreme observations were flagged instead of automatically deleted.

The final master dataset focused on variables relevant to identifying high-performing publishers. Structured game characteristics from games, tags, genres, and categories were therefore prioritized, alongside review, ownership, pricing, and publisher information. Free-text descriptions and promotional assets were excluded because more standardized or analytically relevant representations of the required information were available elsewhere.
