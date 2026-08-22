# Data Preprocessing

The raw Steam data consisted of several separate datasets containing information on games, publishers, reviews, ownership estimates, genres, tags, categories, descriptions, and promotional material. Before the datasets were merged for analysis, each source was assessed and cleaned separately. 

| Dataset            | Main preprocessing                                   | Included in master?       |
| ------------------ | ---------------------------------------------------- | ------------------------- |
| `games.csv`        | Parsing, dates, languages, derived variables         | Yes                       |
| `reviews.csv`      | Parsing, numeric conversion, redundancy removal      | Yes                       |
| `steamspy.csv`     | Company normalization, ownership and price features  | Yes                       |
| `tags.csv`         | Whitespace cleaning and duplicate combination checks | Yes, via aggregated table |
| `genres.csv`       | Multilingual genre standardization                   | Yes, via aggregated table |
| `categories.csv`   | Multilingual category standardization                | Yes, via aggregated table |
| `descriptions.csv` | HTML and text cleaning                               | No                        |
| `promotional.csv`  | Assessed for analytical relevance                    | No                        |

## `games.csv`

The `games.csv` dataset contained the game-level information.

The file was loaded using backslash escaping to handle the source formatting. The `price_overview` variable contained JSON-formatted information. Therefore, the field was parsed and expanded into separate `price_*` columns, while the original nested `price_overview` column was removed from the processed version.

Release dates were standardized by replacing the `"N"` placeholder with a missing value and converting values to a datetime format. The `is_free` variable was converted to Boolean format.

The `languages` field contained HTML and additional formatting information. A separate `full_audio_support` indicator was first extracted from this information. HTML tags, formatting markers, unnecessary whitespace, and the `"N"` placeholder were subsequently removed or standardized in the language field.

Several additional analytical variables were derived from the existing information. These included indicators for whether a game had a recurring subscription and whether it was discounted, as well as a count of the number of supported languages.

### Derived Variables

### Derived Variables

Four additional variables were derived from the cleaned game-level information. `full_audio_support` is a Boolean indicator identifying games whose language information specifies full audio support. `has_recurring_subscription` indicates whether recurring-subscription information is available for a game, while `has_discount` identifies games with a non-zero reported discount percentage. Finally, `language_count` represents the number of supported languages listed for each game.

These variables were derived from information already contained in the source data and were created to provide directly usable characteristics for subsequent analysis.

## `reviews.csv`

The reviews dataset required special parsing because the review text contained backslash-escaped quotation marks that interfered with standard CSV parsing. The file was therefore loaded with an explicit escape character and the Python parsing engine.

Placeholder null values originating from `\N` were normalized by converting the numeric-like variables using numeric coercion. This produced missing values where source values could not be interpreted numerically.

For the `review_score` variable, Steam uses a score of `0` when there are insufficient reviews to assign a review score. These zero values were therefore treated as meaningful information. Five observations in which `review_score` itself was unparseable were removed because the key review metric was unavailable.

Redundancy was checked before columns were removed. The relationship between `review_score` and `review_score_description` was verified, and `total` was confirmed to equal `positive + negative`. Consequently, `review_score_description` and `total` were removed. `steamspy_score_rank` was also removed because more than 99.9% of its observations were missing.

The SteamSpy positive and negative review counts were **not** removed. They disagreed with the official review counts in approximately 18% of observations and were therefore treated as estimates from a separate source.

Numeric variables were converted to appropriate integer or floating-point representations while retaining missing values where necessary. Review text was cleaned by decoding HTML entities, removing HTML tags and normalizing whitespace.

Duplicate records were removed, and the resulting data was validated to ensure that duplicate `app_id`s and complete duplicate rows were no longer present.

## `steamspy.csv`

During import, `app_id` was treated as an integer, while empty strings and `"N"` values were interpreted as missing values. Backslash escaping in the source export was also handled.

Duplicate `app_id` records were identified and removed by retaining the first occurrence, after which the dataset was ordered by `app_id`.

Developer and publisher fields were cleaned by standardizing whitespace and treating empty strings as missing values. Because some fields contained multiple companies, the primary developer and publisher were extracted while preserving the original company fields. Separate normalized company keys were created for grouping by standardizing case and removing legal-form and selected descriptive suffixes.

SteamSpy ownership ranges were parsed into numeric components, and price and initial-price values were converted from cents to euros. Concurrent-user counts were converted to numeric values, with negative values treated as missing.

Four playtime variables contained only zero values throughout the dataset and were therefore removed because they provided no analytical information. The original SteamSpy language and genre fields were retained, while additional count variables were created for analytical use.

Potential data-quality issues were generally flagged rather than removed. In particular, observations where the current price exceeded the initial price and observations with initial prices above €200 were retained and identified using separate indicator variables.

### Derived Variables

Several variables were derived from the cleaned SteamSpy data for subsequent analysis:

* `developer_primary` and `publisher_primary` contain the primary company extracted from developer and publisher fields that may list multiple companies.
* `n_developers` and `n_publishers` record the number of companies listed in the corresponding source fields.
* `developer_key` and `publisher_key` provide normalized company identifiers for consistent analytical grouping.
* `self_published` indicates whether the normalized developer and publisher identifiers correspond to the same company.
* `owners_low` and `owners_high` represent the lower and upper bounds extracted from the SteamSpy ownership range.
* `owners_mid` represents the midpoint of the ownership range and provides a single-value approximation of estimated ownership.
* `owners_mid_log` is a logarithmic transformation of the ownership midpoint, while `owners_bucket` represents the ownership ranges as an ordered categorical variable.
* `price_eur` and `initial_price_eur` contain the current and initial prices converted from cents to euros.
* `discount_pct` contains the reported discount percentage converted to numeric format.
* `is_free` identifies games with a current price of zero.
* `flag_price_inconsistent` identifies observations where the current price exceeds the initial price.
* `discount_implied_pct` represents the discount percentage implied by the current and initial prices.
* `flag_price_outlier` identifies observations with an initial price above €200.
* `n_languages_spy` and `n_genres_spy` represent the numbers of languages and genres listed in the corresponding SteamSpy fields.
* `est_revenue_eur` is a revenue proxy calculated as `owners_mid × price_eur`.
* `is_investable` identifies observations for which publisher, price, and ownership information are all available.

`est_revenue_eur` should be interpreted as an approximation rather than actual revenue. SteamSpy ownership figures are provided as ranges, and the calculation uses the range midpoint and current price. It therefore does not account for factors such as historical or regional pricing, refunds, bundles, free-to-play behavior, or Steam's revenue share.

These derived variables were constructed from information already contained in the source data. Their analytical selection, interpretation, and use in evaluating publisher performance are discussed separately in the methodology.

## `tags.csv`

The tags dataset was inspected for its structure, data types, missing values, duplicate rows, leading and trailing whitespace, empty strings, and inconsistent capitalization.

Because an individual game can legitimately have multiple tags, multiple observations for the same `app_id` were intentionally preserved. Only duplicate combinations of `app_id` and tag were considered redundant.

Tag values were stripped of leading and trailing whitespace, and the cleaning procedure included removal of empty tags and duplicate `app_id`–tag combinations where present. The original Steam naming conventions were deliberately retained.

The quality assessment ultimately found no material data-quality problems requiring observations to be removed.

## `genres.csv`

The genres dataset was similarly assessed for missing values, duplicates, whitespace, empty values, capitalization inconsistencies, and variation in categorical labels.

The principal issue was that equivalent genres appeared under different languages and naming conventions. A mapping dictionary was therefore used to standardize multilingual labels into consistent English categories. For example, different language variants referring to Action, Adventure, Casual, Indie, RPG, Simulation, Sports, and Strategy were mapped to common English labels.

Multiple genres for an individual game were intentionally retained because they represent valid many-to-many relationships. Following standardization, however, different source labels could map to the same English genre for the same game. Duplicate `app_id`–genre combinations created through this process were therefore removed.

The standardization reduced **121 original genre labels to 33 consistent English genre categories**. According to the preprocessing validation, no missing values or duplicate `app_id`–genre combinations remained after cleaning.

## `categories.csv`

The categories dataset contained a similar multilingual standardization problem. Initial checks covered missing values, duplicates, whitespace, empty values, case inconsistencies, and the range of unique categories.

Two rounds of mapping were used to consolidate equivalent multilingual labels into standardized English categories. Importantly, standardization was based on functional equivalence rather than simply grouping similar concepts. Categories representing genuinely different Steam features were kept separate. For example, `PvP`, `Online PvP`, and `Shared/Split Screen PvP` remained distinct, as did the corresponding Co-op categories and different forms of VR functionality.

The process reduced **315 original category labels to 42 standardized English categories**. Because several original labels could map to the same standardized category for a game, the mapping process generated redundant `app_id`–category combinations. These duplicates were removed after standardization, resulting in the removal of **79 redundant rows**.

## Aggregation of Tags, Categories, and Genres

Following individual cleaning, the tags, genres, and categories datasets remained in long format, with multiple valid observations per `app_id`. For integration into the game-level master dataset, each dataset was subsequently aggregated to one row per `app_id`, retaining all associated categorical values. The aggregated datasets were then validated to confirm that each `app_id` occurred only once before being combined using outer joins.

The resulting combined categories–tags–genres table therefore provided a game-level representation of these many-to-many characteristics without creating multiple rows per game. The merged table was validated to confirm that it contained no duplicate `app_id` values and that its row count corresponded to the union of identifiers across the three input datasets. This intermediate table was used as one of the inputs to the construction of the final master dataset.

## `descriptions.csv`

The descriptions dataset contained the text fields `summary`, `extensive`, and `about`. A data-quality procedure was designed to inspect the dataset's shape, data types, missing values, duplicate rows and `app_id`s, empty text fields, remaining HTML, description lengths, and very short descriptions.

HTML was removed from each of the three description fields using BeautifulSoup while preserving the underlying textual content. Following HTML removal, records with fewer than 20 characters in any of the specified description fields were filtered from the processed version.

However, the descriptions dataset was ultimately **excluded from the merged master dataset**. The information relevant to the analytical objective was already represented through more standardized variables in the genres, tags, and categories datasets. These structured categorical variables were preferred over free-form descriptions for the subsequent publisher analysis.

## `promotional.csv`

The promotional dataset was **excluded from the master dataset without being used as an analytical input**. It consists primarily of promotional and marketing-related information, including links to marketing images.

These variables were considered outside the scope of the analysis. The objective of the project is to identify and evaluate **high-performing publishers**, and the promotional fields did not provide relevant measures for evaluating publisher performance within the chosen analytical strategy.

## Master Dataset Construction

After the individual datasets were cleaned, the processed data were combined into a single `master_dataset.csv` file for subsequent analysis. The master dataset was constructed from four processed sources: game-level information, reviews, SteamSpy information, and a previously aggregated dataset containing categories, tags, and genres.

All datasets were merged on `app_id` using outer joins. This approach preserved the union of game identifiers across all sources, meaning that a game was retained even when it was unavailable in one or more of the contributing datasets. Before merging, the `app_id` field was verified to have integer representation across all four sources.

Placeholder text values representing missing information, including values such as `"None"`, `"Unknown"`, `"N/A"`, `"-"`, and `"--"`, were standardized to missing values before the merge. This ensured that placeholder values were correctly treated as missing data rather than as valid text entries. 

Several sources contained variables representing similar concepts. Rather than assuming that these variables were equivalent, the source-specific versions were retained and given explicit names. In particular, genre information from the categories/tags/genres dataset and SteamSpy was retained separately, as were language and free-to-play indicators from the games and SteamSpy datasets. Official and SteamSpy review counts were similarly preserved as separate measures. This prevented potentially meaningful differences between independently collected sources from being lost during the merge.

Four provenance indicators were added to identify whether each `app_id` was present in the games, categories/tags/genres, reviews, and SteamSpy sources. These indicators allow structural absence from a source to be distinguished from a missing field within an otherwise present source record.

Missing values were generally retained rather than imputed. One exception concerned price information for games explicitly identified as free in the games dataset. Where the corresponding price was missing, separate cleaned price variables were created in which these values were assigned a price of zero. The original price variables were preserved unchanged. Missing prices for games not identified as free remained missing because their values could not be inferred from the available information.

The completed master dataset was validated for duplicate `app_id` values, duplicate full rows, missingness, and consistency between overlapping source variables. No normalization, scaling, or categorical encoding was applied during master-dataset construction, because these transformations depend on the subsequent analytical method and were therefore kept separate from the reusable master dataset.

## AI-assisted Preprocessing

Generative AI tools were used to assist with portions of the preprocessing code, including data-quality checks, categorical standardization, and dataset integration. Prompts specified the required cleaning rules, constraints, and validation procedures. The resulting code was reviewed and adjusted as necessary before being incorporated into the preprocessing pipeline.

## Overall Preprocessing Approach

Across the datasets, preprocessing followed a conservative approach. Information was standardized where inconsistent formatting or multilingual labels would otherwise prevent meaningful comparison. Redundant variables were removed only when their redundancy was established, while variables representing similar information from different sources were retained. Missing values were preserved rather than imputed, and unusual or extreme observations were flagged instead of automatically deleted.

The final master dataset brought together the cleaned game, publisher, review, ownership, pricing, and structured game-characteristic information required for subsequent analysis. Structured game characteristics from games, tags, genres, and categories were therefore prioritized, alongside review, ownership, pricing, and publisher information. Free-text descriptions and promotional assets were excluded because more standardized or analytically relevant representations of the required information were available elsewhere.
