# Data Preprocessing

The raw Steam data consisted of several separate datasets containing information on games, publishers, reviews, ownership estimates, genres, tags, categories, descriptions, and promotional material. 

Before the datasets were merged for analysis, each source was assessed and cleaned separately. 

## Preprocessing Overview

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

## Preprocessing Principles

Preprocessing followed a conservative approach across all datasets:

* Information was standardized where inconsistent formatting or multilingual labels would otherwise prevent meaningful comparison.
* Redundant variables were removed only when their redundancy was established.
* Variables representing similar information from different sources were retained.
* Missing values were generally preserved rather than imputed.
* Unusual or extreme observations were flagged instead of automatically deleted.

The final master dataset combines the cleaned game, publisher, review, ownership, pricing, and structured game-characteristic information required for subsequent analysis.

Structured game characteristics from games, tags, genres, and categories were prioritized alongside review, ownership, pricing, and publisher information. Free-text descriptions and promotional assets were excluded because more standardized or analytically relevant representations of the required information were available elsewhere.

---

## `games.csv`

The `games.csv` dataset contained the game-level information.

### Cleaning

The following preprocessing steps were applied:

* The file was loaded using backslash escaping to handle the source formatting.
* The JSON-formatted `price_overview` field was parsed and expanded into separate `price_*` columns.
* The original nested `price_overview` column was removed from the processed version.
* The `"N"` placeholder in release dates was replaced with a missing value.
* Release dates were converted to a datetime format.
* `is_free` was converted to Boolean format.
* A `full_audio_support` indicator was extracted from the `languages` field.
* HTML tags, formatting markers, unnecessary whitespace, and the `"N"` placeholder were removed or standardized in the language field.

### Derived Variables

Four additional variables were derived from the cleaned game-level information.

| Variable                     | Description                                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------- |
| `full_audio_support`         | Boolean indicator identifying games whose language information specifies full audio support |
| `has_recurring_subscription` | Indicates whether recurring-subscription information is available for a game                |
| `has_discount`               | Identifies games with a non-zero reported discount percentage                               |
| `language_count`             | Number of supported languages listed for each game                                          |

These variables were derived from information already contained in the source data and were created to provide directly usable characteristics for subsequent analysis.

---

## `reviews.csv`

The reviews dataset required special parsing because the review text contained backslash-escaped quotation marks that interfered with standard CSV parsing. 

### Cleaning

* The file was loaded using an explicit escape character and the Python parsing engine.
* Placeholder null values originating from `\N` were normalized by converting numeric-like variables using numeric coercion.
* Values that could not be interpreted numerically were converted to missing values.
* Numeric variables were converted to appropriate integer or floating-point representations while retaining missing values where necessary.
* Review text was cleaned by:

  * decoding HTML entities,
  * removing HTML tags, and
  * normalizing whitespace.
* Duplicate records were removed.

### Review Score Handling

Steam uses a `review_score` of `0` when there are insufficient reviews to assign a review score. These zero values were therefore retained as meaningful information.

Five observations in which `review_score` itself was unparseable were removed because the key review metric was unavailable.

### Redundancy Assessment

Redundancy was checked before columns were removed.

The following relationships were verified:

* `review_score_description` was redundant with `review_score`.
* `total` was confirmed to equal `positive + negative`.

Consequently:

* `review_score_description` was removed.
* `total` was removed.
* `steamspy_score_rank` was removed because more than 99.9% of its observations were missing.

### Decision: Retain SteamSpy Review Counts

The SteamSpy positive and negative review counts were **not removed**.

They disagreed with the official review counts in approximately 18% of observations and were therefore treated as estimates from a separate source.

### Validation

The processed dataset was validated to ensure that:

* duplicate `app_id` values were no longer present, and
* complete duplicate rows were no longer present.

---

## `steamspy.csv`

The SteamSpy dataset contained publisher, developer, ownership, pricing, language, genre, and other game-level information.

### Import and Identifier Cleaning

* `app_id` was treated as an integer during import.
* Empty strings and `"N"` values were interpreted as missing values.
* Backslash escaping in the source export was handled.
* Duplicate `app_id` records were identified and removed by retaining the first occurrence.
* The resulting dataset was ordered by `app_id`.

### Developer and Publisher Cleaning

Developer and publisher fields were cleaned by:

* standardizing whitespace, and
* treating empty strings as missing values.

Because some fields contained multiple companies:

* the primary developer and publisher were extracted,
* the original company fields were preserved, and
* separate normalized company keys were created for grouping.

Company keys were normalized by standardizing case and removing legal-form and selected descriptive suffixes.

### Ownership and Price Cleaning

* SteamSpy ownership ranges were parsed into numeric components.
* Price and initial-price values were converted from cents to euros.
* Concurrent-user counts were converted to numeric values.
* Negative concurrent-user values were treated as missing.

Four playtime variables contained only zero values throughout the dataset. These variables were removed because they provided no analytical information.

The original SteamSpy language and genre fields were retained, while additional count variables were created for analytical use.

### Data-Quality Flags

Potential data-quality issues were generally **flagged rather than removed**.

In particular:

* observations where the current price exceeded the initial price were retained and flagged;
* observations with initial prices above €200 were retained and flagged.

### Derived Variables

| Variable                  | Description                                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------------------- |
| `developer_primary`       | Primary company extracted from developer fields that may list multiple companies                    |
| `publisher_primary`       | Primary company extracted from publisher fields that may list multiple companies                    |
| `n_developers`            | Number of companies listed in the developer field                                                   |
| `n_publishers`            | Number of companies listed in the publisher field                                                   |
| `developer_key`           | Normalized developer identifier for consistent analytical grouping                                  |
| `publisher_key`           | Normalized publisher identifier for consistent analytical grouping                                  |
| `self_published`          | Indicates whether the normalized developer and publisher identifiers correspond to the same company |
| `owners_low`              | Lower bound extracted from the SteamSpy ownership range                                             |
| `owners_high`             | Upper bound extracted from the SteamSpy ownership range                                             |
| `owners_mid`              | Midpoint of the ownership range, providing a single-value approximation of estimated ownership      |
| `owners_mid_log`          | Logarithmic transformation of the ownership midpoint                                                |
| `owners_bucket`           | Ownership ranges represented as an ordered categorical variable                                     |
| `price_eur`               | Current price converted from cents to euros                                                         |
| `initial_price_eur`       | Initial price converted from cents to euros                                                         |
| `discount_pct`            | Reported discount percentage converted to numeric format                                            |
| `is_free`                 | Identifies games with a current price of zero                                                       |
| `flag_price_inconsistent` | Identifies observations where the current price exceeds the initial price                           |
| `discount_implied_pct`    | Discount percentage implied by the current and initial prices                                       |
| `flag_price_outlier`      | Identifies observations with an initial price above €200                                            |
| `n_languages_spy`         | Number of languages listed in the SteamSpy language field                                           |
| `n_genres_spy`            | Number of genres listed in the SteamSpy genre field                                                 |
| `est_revenue_eur`         | Revenue proxy calculated as `owners_mid × price_eur`                                                |
| `is_investable`           | Identifies observations for which publisher, price, and ownership information are all available     |

### Revenue Proxy

`est_revenue_eur` should be interpreted as an approximation rather than actual revenue.

SteamSpy ownership figures are provided as ranges, and the calculation uses the range midpoint and current price. It therefore does not account for:

* historical pricing,
* regional pricing,
* refunds,
* bundles,
* free-to-play behavior, or
* Steam's revenue share.

These derived variables were constructed from information already contained in the source data. Their analytical selection, interpretation, and use in evaluating publisher performance are discussed separately in the methodology.

---

## `tags.csv`

The tags dataset was inspected for:

* structure,
* data types,
* missing values,
* duplicate rows,
* leading and trailing whitespace,
* empty strings, and
* inconsistent capitalization.

### Cleaning

An individual game can legitimately have multiple tags. Multiple observations for the same `app_id` were therefore intentionally preserved.

Only duplicate combinations of `app_id` and tag were considered redundant.

Tag values were:

* stripped of leading and trailing whitespace;
* checked for empty values; and
* checked for duplicate `app_id`–tag combinations.

The original Steam naming conventions were deliberately retained.

### Validation

The quality assessment found no material data-quality problems requiring observations to be removed.

---

## `genres.csv`

The genres dataset was assessed for:

* missing values,
* duplicates,
* whitespace,
* empty values,
* capitalization inconsistencies, and
* variation in categorical labels.

### Multilingual Standardization

The principal issue was that equivalent genres appeared under different languages and naming conventions.

A mapping dictionary was therefore used to standardize multilingual labels into consistent English categories. For example, different language variants referring to the following genres were mapped to common English labels:

* Action
* Adventure
* Casual
* Indie
* RPG
* Simulation
* Sports
* Strategy

Multiple genres for an individual game were intentionally retained because they represent valid many-to-many relationships.

Following standardization, different source labels could map to the same English genre for the same game. Duplicate `app_id`–genre combinations created through this process were therefore removed.

### Result and Validation

The standardization reduced **121 original genre labels to 33 consistent English genre categories**.

After cleaning:

* no missing values remained; and
* no duplicate `app_id`–genre combinations remained.

---

## `categories.csv`

The categories dataset contained a similar multilingual standardization problem.

Initial checks covered:

* missing values,
* duplicates,
* whitespace,
* empty values,
* case inconsistencies, and
* the range of unique categories.

### Multilingual Standardization

Two rounds of mapping were used to consolidate equivalent multilingual labels into standardized English categories.

Standardization was based on **functional equivalence**, rather than simply grouping similar concepts. Categories representing genuinely different Steam features were kept separate.

For example:

* `PvP`,
* `Online PvP`, and
* `Shared/Split Screen PvP`

remained distinct.

The corresponding Co-op categories and different forms of VR functionality were also kept separate.

### Result and Validation

The standardization reduced **315 original category labels to 42 standardized English categories**.

Because several original labels could map to the same standardized category for a game, the mapping process generated redundant `app_id`–category combinations.

These duplicates were removed after standardization, resulting in the removal of **79 redundant rows**.

---

## Aggregation of Tags, Categories, and Genres

Following individual cleaning, the tags, genres, and categories datasets remained in long format, with multiple valid observations per `app_id`.

### Aggregation

For integration into the game-level master dataset:

1. Each dataset was aggregated to one row per `app_id`.
2. All associated categorical values were retained.
3. The aggregated datasets were validated to confirm that each `app_id` occurred only once.
4. The datasets were combined using outer joins.

The resulting categories–tags–genres table provided a game-level representation of these many-to-many characteristics without creating multiple rows per game.

### Validation

The merged table was validated to confirm that:

* it contained no duplicate `app_id` values; and
* its row count corresponded to the union of identifiers across the three input datasets.

This intermediate table was used as one of the inputs to the construction of the final master dataset.

---

## `descriptions.csv`

The descriptions dataset contained three text fields:

* `summary`,
* `extensive`, and
* `about`.

### Data-Quality Assessment

The data-quality procedure was designed to inspect:

* dataset shape,
* data types,
* missing values,
* duplicate rows,
* duplicate `app_id` values,
* empty text fields,
* remaining HTML,
* description lengths, and
* very short descriptions.

### Cleaning

HTML was removed from all three description fields using BeautifulSoup while preserving the underlying textual content.

Following HTML removal, records with fewer than 20 characters in any of the specified description fields were filtered from the processed version.

### Decision: Excluded from the Master Dataset

The descriptions dataset was ultimately **excluded from the merged master dataset**.

The information relevant to the analytical objective was already represented through more standardized variables in the genres, tags, and categories datasets. These structured categorical variables were preferred over free-form descriptions for the subsequent publisher analysis.

---

## `promotional.csv`

The promotional dataset consists primarily of promotional and marketing-related information, including links to marketing images.

### Decision: Excluded from the Master Dataset

The promotional dataset was **excluded from the master dataset without being used as an analytical input**.

These variables were considered outside the scope of the analysis. The objective of the project is to identify and evaluate **high-performing publishers**, and the promotional fields did not provide relevant measures for evaluating publisher performance within the chosen analytical strategy.

---

## Master Dataset Construction

After the individual datasets were cleaned, the processed data were combined into a single `master_dataset.csv` file for subsequent analysis.

### Inputs

The master dataset was constructed from four processed sources:

| Source                                    | Information                                            |
| ----------------------------------------- | ------------------------------------------------------ |
| Games                                     | Game-level information                                 |
| Reviews                                   | Review information                                     |
| SteamSpy                                  | Publisher, ownership, pricing, and related information |
| Aggregated categories–tags–genres dataset | Structured game characteristics                        |

### Merge Strategy

All datasets were merged on `app_id` using **outer joins**.

This approach preserved the union of game identifiers across all sources. A game was therefore retained even when it was unavailable in one or more of the contributing datasets.

Before merging, `app_id` was verified to have integer representation across all four sources.

### Missing-Value Standardization

Placeholder text values representing missing information were standardized to missing values before the merge.

These included:

* `"None"`
* `"Unknown"`
* `"N/A"`
* `"-"`
* `"--"`

This ensured that placeholder values were treated as missing data rather than valid text entries.

### Overlapping Source Variables

Several sources contained variables representing similar concepts. These variables were **not assumed to be equivalent**.

Instead, source-specific versions were retained and given explicit names.

In particular:

* genre information from the categories/tags/genres dataset and SteamSpy was retained separately;
* language information from the games and SteamSpy datasets was retained separately;
* free-to-play indicators from the games and SteamSpy datasets were retained separately; and
* official and SteamSpy review counts were retained as separate measures.

This prevented potentially meaningful differences between independently collected sources from being lost during the merge.

### Provenance Indicators

Four provenance indicators were added to identify whether each `app_id` was present in:

* games,
* categories/tags/genres,
* reviews, and
* SteamSpy.

These indicators allow structural absence from a source to be distinguished from a missing field within an otherwise present source record.

### Missing-Value Handling

Missing values were generally retained rather than imputed.

One exception concerned price information for games explicitly identified as free in the games dataset.

Where the corresponding price was missing:

* separate cleaned price variables were created; and
* the missing price was assigned a value of zero.

The original price variables were preserved unchanged.

Missing prices for games not identified as free remained missing because their values could not be inferred from the available information.

### Validation

The completed master dataset was validated for:

* duplicate `app_id` values,
* duplicate full rows,
* missingness, and
* consistency between overlapping source variables.

### Transformations Intentionally Deferred

The following transformations were **not applied** during master-dataset construction:

* normalization,
* scaling, and
* categorical encoding.

These transformations depend on the subsequent analytical method and were therefore kept separate from the reusable master dataset.

---

## AI-Assisted Preprocessing

Generative AI tools were used to assist with portions of the preprocessing code, including:

* data-quality checks,
* categorical standardization, and
* dataset integration.

Prompts specified the required cleaning rules, constraints, and validation procedures.

The resulting code was reviewed and adjusted as necessary before being incorporated into the preprocessing pipeline.
