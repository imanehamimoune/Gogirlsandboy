# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 17:49:03 2026

@author: lqn21
"""

"""
# ====================================================================
# PROMPT
# ====================================================================

Model Role: You are an expert Data Analyst and Python/Pandas Data Engineer 
specializing in data profiling, cleaning, categorical standardization, 
transformation, and data-quality validation.

Context: I will provide three CSV files: tags.csv, genres.csv, and categories.csv. 
Your task is to inspect, clean, standardize, validate, and export each dataset 
separately using Python and Pandas.

Expected Outcome:
- Inspect the first rows, shape, column names, and data types.
- Check missing values and duplicate rows.
- Check leading/trailing whitespace, empty strings, and inconsistent text formatting.
- Identify the relevant columns.
- Preserve multiple rows for the same app_id, because one game may have multiple tags, genres, or categories.
- Remove duplicate app_id + value combinations only where justified.
- For categories, keep genuinely different features separate, such as: 
  PvP, Online PvP, LAN PvP, Shared/Split Screen PvP
  Co-op, Online Co-op, LAN Co-op, Shared/Split Screen Co-op
  VR Only and VR Support
- Do not delete unusual values without a clear reason.
- Do not invent or arbitrarily replace data.

Validation:
For each dataset:
- Print final shape.
- Print missing values.
- Print duplicate rows.
- Print the number of unique categorical values.
- Print a cleaning summary with original rows, final rows, and rows removed.
- Reset the index after cleaning where necessary.

Output Requirements:
- Use Python and Pandas.
- Make the code readable, reproducible, and executable in Spyder.
- Never overwrite the original files.
- Save the cleaned outputs as:
  tags_cleaned.csv
  genres_cleaned.csv
  categories_cleaned.csv
  
Follow-up Adjustments:
- Keep the original Steam naming conventions for tags and avoid unnecessary renaming.
- For genres and categories, standardize multilingual labels into English using a mapping dictionary.
- For categories, use additional mapping rules where required, while keeping functionally different categories separate.
- After standardization, remove duplicate app_id + genre/category combinations if created.
- Use the local file paths provided in Spyder.
- For genres and categories, also calculate the Top 5 values by number of unique
  games and the percentage of games represented by each after cleaning.

Request: Clean the three CSV datasets according to the rules above.
Author: Tung-Jui Lin (Prompt and Adjustments)
"""

import pandas as pd

# ====================================================================
# TAGS
# ====================================================================

# =====================================================
# 1. LOAD DATA
# =====================================================

tags = pd.read_csv("data/raw/tags.zip")

original_rows = len(tags)


# =====================================================
# 2. INITIAL DATA CHECK
# =====================================================

print("----- INITIAL DATA CHECK -----")

print("\nFirst 5 rows:")
print(tags.head())

print("\nShape:")
print(tags.shape)

print("\nColumns:")
print(tags.columns)

print("\nData types:")
tags.info()

print("\nMissing values:")
print(tags.isnull().sum())

print("\nDuplicate rows:")
print(tags.duplicated().sum())

print("\nNumber of unique tags:")
print(tags["tag"].nunique())


# =====================================================
# 3. CHECK TEXT QUALITY
# =====================================================

print("\nTags with leading/trailing spaces:")
print(
    (tags["tag"] != tags["tag"].str.strip()).sum()
)

print("\nEmpty tags:")
print(
    (tags["tag"].str.strip() == "").sum()
)


# =====================================================
# 4. CHECK CASE INCONSISTENCIES
# =====================================================

tags_check = tags.copy()

tags_check["tag_lower"] = tags_check["tag"].str.lower()

case_variations = (
    tags_check.groupby("tag_lower")["tag"]
    .unique()
)

case_variations = case_variations[
    case_variations.apply(len) > 1
]

print("\nCase inconsistencies:")
print(case_variations)


# =====================================================
# 5. DATA CLEANING
# =====================================================

# Remove leading/trailing spaces
tags["tag"] = tags["tag"].str.strip()

# Remove empty tags
tags = tags[tags["tag"] != ""]

# Remove duplicate app_id-tag combinations
tags = tags.drop_duplicates(
    subset=["app_id", "tag"]
)

# Reset index
tags = tags.reset_index(drop=True)


# =====================================================
# 6. FINAL VALIDATION
# =====================================================

print("\n----- FINAL VALIDATION -----")

print("\nFinal shape:")
print(tags.shape)

print("\nMissing values:")
print(tags.isnull().sum())

print("\nDuplicate rows:")
print(tags.duplicated().sum())

print("\nEmpty tags:")
print((tags["tag"] == "").sum())

print("\nNumber of unique tags:")
print(tags["tag"].nunique())


# =====================================================
# 7. CLEANING SUMMARY
# =====================================================

print("\n----- CLEANING SUMMARY -----")

print("Original rows:", original_rows)
print("Final rows:", len(tags))
print("Rows removed:", original_rows - len(tags))


# =====================================================
# 8. EXPORT CLEANED DATA
# =====================================================

tags.to_csv("data/processed/tags_cleaned.csv", index=False)

print("\nTags data cleaning completed successfully.")

#Conclusion:
#The tags dataset was checked for missing values, duplicates, empty strings, 
#leading/trailing whitespace, and case inconsistencies. 
#No data quality issues were identified, so no observations were removed.


# ====================================================================
# GENRES
# ====================================================================

# =====================================================
# 1. LOAD DATA
# =====================================================

genres = pd.read_csv("data/raw/genres.zip")

original_rows = len(genres)


# =====================================================
# 2. INITIAL DATA CHECK
# =====================================================

print("----- INITIAL DATA CHECK -----")

print("\nFirst 5 rows:")
print(genres.head())

print("\nShape:")
print(genres.shape)

print("\nColumns:")
print(genres.columns)

print("\nData types:")
genres.info()

print("\nMissing values:")
print(genres.isnull().sum())

print("\nDuplicate rows:")
print(genres.duplicated().sum())

# =====================================================
# 3. CHECK GENRE VALUES
# =====================================================

print("\nNumber of unique genres:")
print(genres["genre"].nunique())

print("\nUnique genres:")
print(sorted(genres["genre"].unique()))


# =====================================================
# 4. CHECK TEXT QUALITY
# =====================================================

print("\nGenres with leading/trailing spaces:")
print(
    (genres["genre"] != genres["genre"].str.strip()).sum()
)

print("\nEmpty genres:")
print(
    (genres["genre"].str.strip() == "").sum()
)


# =====================================================
# 5. CHECK CASE INCONSISTENCIES
# =====================================================

genres_check = genres.copy()

genres_check["genre_lower"] = genres_check["genre"].str.lower()

case_variations = (
    genres_check.groupby("genre_lower")["genre"]
    .unique()
)

case_variations = case_variations[
    case_variations.apply(len) > 1
]

print("\nCase inconsistencies:")
print(case_variations)

# =====================================================
# 6. STANDARDIZE GENRE NAMES
# =====================================================

genre_mapping = {

    # Action
    "Acción": "Action",
    "Azione": "Action",
    "Ação": "Action",
    "Actie": "Action",
    "Akcja": "Action",
    "Akční": "Action",
    "Бойовики": "Action",
    "Экшены": "Action",
    "アクション": "Action",
    "动作": "Action",
    "動作": "Action",

    # Adventure
    "Abenteuer": "Adventure",
    "Aventura": "Adventure",
    "Aventure": "Adventure",
    "Avontuur": "Adventure",
    "Avventura": "Adventure",
    "Dobrodružné": "Adventure",
    "Eventyr": "Adventure",
    "Seikkailu": "Adventure",
    "Пригоди": "Adventure",
    "Приключенческие игры": "Adventure",
    "アドベンチャー": "Adventure",
    "冒险": "Adventure",
    "冒險": "Adventure",

    # Casual
    "Gelegenheitsspiele": "Casual",
    "Occasionnel": "Casual",
    "Passatempo": "Casual",
    "Казуальные игры": "Casual",
    "Казуальні ігри": "Casual",
    "カジュアル": "Casual",
    "休闲": "Casual",
    "休閒": "Casual",

    # Early Access
    "Acceso anticipado": "Early Access",
    "Ранний доступ": "Early Access",
    "抢先体验": "Early Access",
    "搶先體驗": "Early Access",

    # Free to Play
    "Free To Play": "Free to Play",
    "Free-to-play": "Free to Play",
    "Grátis para Jogar": "Free to Play",
    "Kostenlos spielbar": "Free to Play",
    "Бесплатные": "Free to Play",
    "免费开玩": "Free to Play",
    "無料プレイ": "Free to Play",

    # Indie
    "Indépendant": "Indie",
    "Niezależne": "Indie",
    "Інді": "Indie",
    "Инди": "Indie",
    "インディー": "Indie",
    "独立": "Indie",
    "獨立製作": "Indie",

    # Massively Multiplayer
    "MMO": "Massively Multiplayer",
    "Massivement multijoueur": "Massively Multiplayer",
    "Multijugador masivo": "Massively Multiplayer",
    "Многопользовательские игры": "Massively Multiplayer",
    "大型多人連線": "Massively Multiplayer",

    # Racing
    "Carreras": "Racing",
    "Course automobile": "Racing",
    "Race": "Racing",
    "Гонки": "Racing",

    # RPG
    "GDR": "RPG",
    "Rol": "RPG",
    "Rollenspiel": "RPG",
    "Roolipelit": "RPG",
    "Ролевые игры": "RPG",
    "角色扮演": "RPG",

    # Simulation
    "Simulaatio": "Simulation",
    "Simuladores": "Simulation",
    "Simulatie": "Simulation",
    "Simulationen": "Simulation",
    "Simulação": "Simulation",
    "Simulering": "Simulation",
    "Симуляторы": "Simulation",
    "模拟": "Simulation",
    "模擬": "Simulation",

    # Sports
    "Deportes": "Sports",
    "Sport": "Sports",
    "Спортивные игры": "Sports",
    "体育": "Sports",

    # Strategy
    "Estrategia": "Strategy",
    "Estratégia": "Strategy",
    "Strategi": "Strategy",
    "Strategia": "Strategy",
    "Strategie": "Strategy",
    "Stratégie": "Strategy",
    "Стратегии": "Strategy",
    "ストラテジー": "Strategy",
    "策略": "Strategy",

    # Utilities
    "Utilidades": "Utilities"
}

genres["genre"] = genres["genre"].replace(genre_mapping)

print("\nUnique genres after full standardization:")
print(sorted(genres["genre"].unique()))

print("\nNumber of unique genres after full standardization:")
print(genres["genre"].nunique())

# =====================================================
# 7. REMOVE DUPLICATES AFTER STANDARDIZATION
# =====================================================

genres = genres.drop_duplicates(
    subset=["app_id", "genre"]
)

genres = genres.reset_index(drop=True)


# =====================================================
# 8. FINAL VALIDATION
# =====================================================

print("\n----- FINAL VALIDATION -----")

print("\nFinal shape:")
print(genres.shape)

print("\nMissing values:")
print(genres.isnull().sum())

print("\nDuplicate rows:")
print(genres.duplicated().sum())

print("\nNumber of unique genres:")
print(genres["genre"].nunique())

print("\nFinal unique genres:")
print(sorted(genres["genre"].unique()))


# =====================================================
# 9. CLEANING SUMMARY
# =====================================================

print("\n----- CLEANING SUMMARY -----")

print("Original rows:", original_rows)
print("Final rows:", len(genres))
print("Rows removed:", original_rows - len(genres))


# =====================================================
# 10. EXPORT CLEANED DATA
# =====================================================

genres.to_csv("data/processed/genres_cleaned.csv", index=False)

print("\nGenres data cleaning completed successfully.")

#Conclusion:
#The genres dataset initially contained 121 unique genre labels, 
#including multiple language variants and inconsistent naming conventions. 
#These labels were standardized into 33 consistent English genre categories. 
#No missing values or duplicate app_id–genre combinations remained after cleaning, 
#and no observations needed to be removed.

#=======================================================
# 11. Top 5
#=======================================================

top5_genres = genres["genre"].value_counts().head(5)

print("\nTop 5 Genres:")
print(top5_genres)

total_games = genres["app_id"].nunique()

top5_genres_by_games = (
    genres.groupby("genre")["app_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(5)
)

top5_genres_game_pct = (
    top5_genres_by_games / total_games * 100
)

print("\nTop 5 Genres by Number of Games:")
print(top5_genres_by_games)

print("\nPercentage of Games:")
print(top5_genres_game_pct)

#Top 5 Genres:
#Genre        Amount     Percent(%)
#Indie         86480     70.620131
#Action        52837     43.147038
#Adventure     50910     41.573437
#Casual        48655     39.731990
#Simulation    24952     20.375966


# ====================================================================
# CATEGORIES
# ====================================================================

# =====================================================
# 1. LOAD DATA
# =====================================================

categories = pd.read_csv("data/raw/categories.zip")

original_rows = len(categories)


# =====================================================
# 2. INITIAL DATA CHECK
# =====================================================

print("----- INITIAL DATA CHECK -----")

print("\nFirst 5 rows:")
print(categories.head())

print("\nShape:")
print(categories.shape)

print("\nColumns:")
print(categories.columns)

print("\nData types:")
categories.info()

print("\nMissing values:")
print(categories.isnull().sum())

print("\nDuplicate rows:")
print(categories.duplicated().sum())

# =====================================================
# 3. CHECK CATEGORY VALUES
# =====================================================

print("\nNumber of unique categories:")
print(categories["category"].nunique())

print("\nUnique categories:")
print(sorted(categories["category"].unique()))


# =====================================================
# 4. CHECK TEXT QUALITY
# =====================================================

print("\nCategories with leading/trailing spaces:")
print(
    (categories["category"] != categories["category"].str.strip()).sum()
)

print("\nEmpty categories:")
print(
    (categories["category"].str.strip() == "").sum()
)


# =====================================================
# 5. CHECK CASE INCONSISTENCIES
# =====================================================

categories_check = categories.copy()

categories_check["category_lower"] = (
    categories_check["category"].str.lower()
)

case_variations = (
    categories_check.groupby("category_lower")["category"]
    .unique()
)

case_variations = case_variations[
    case_variations.apply(len) > 1
]

print("\nCase inconsistencies:")
print(case_variations)

# =====================================================
# 6. STANDARDIZE CATEGORY NAMES
# =====================================================

category_mapping = {

    # -------------------------------------------------
    # Single-player
    # -------------------------------------------------
    "Singleplayer": "Single-player",
    "Einzelspieler": "Single-player",
    "Enkeltspiller": "Single-player",
    "Giocatore singolo": "Single-player",
    "Jednoosobowa": "Single-player",
    "Režim pro jednoho hráče": "Single-player",
    "Solo": "Single-player",
    "Um jogador": "Single-player",
    "Un jugador": "Single-player",
    "Yksinpeli": "Single-player",
    "Для одного игрока": "Single-player",
    "Однокористувацька гра": "Single-player",
    "シングルプレイヤー": "Single-player",
    "单人": "Single-player",
    "單人": "Single-player",

    # -------------------------------------------------
    # Multi-player
    # -------------------------------------------------
    "Multiplayer": "Multi-player",
    "Mehrspieler": "Multi-player",
    "Moninpeli": "Multi-player",
    "Multigiocatore": "Multi-player",
    "Multijogador": "Multi-player",
    "Multijoueur": "Multi-player",
    "Multijugador": "Multi-player",
    "Wieloosobowa": "Multi-player",
    "Для нескольких игроков": "Multi-player",
    "マルチプレイヤー": "Multi-player",
    "多人": "Multi-player",

    # -------------------------------------------------
    # Family Sharing
    # -------------------------------------------------
    "Compartilhamento em família": "Family Sharing",
    "Condivisione familiare": "Family Sharing",
    "Familiedeling": "Family Sharing",
    "Familienbibliothek": "Family Sharing",
    "Gezinsbibliotheek": "Family Sharing",
    "Partage familial": "Family Sharing",
    "Partilha de Biblioteca": "Family Sharing",
    "Perhejako": "Family Sharing",
    "Préstamo familiar": "Family Sharing",
    "Sdílení v rodině": "Family Sharing",
    "Udostępnianie gier": "Family Sharing",
    "Семейный доступ": "Family Sharing",
    "Сімейна бібліотека": "Family Sharing",
    "ファミリーシェアリング": "Family Sharing",
    "家庭共享": "Family Sharing",
    "親友同享": "Family Sharing",

    # -------------------------------------------------
    # Steam Achievements
    # -------------------------------------------------
    "Achievement di Steam": "Steam Achievements",
    "Achievementy": "Steam Achievements",
    "Conquistas Steam": "Steam Achievements",
    "Logros de Steam": "Steam Achievements",
    "Osiągnięcia Steam": "Steam Achievements",
    "Proezas do Steam": "Steam Achievements",
    "Steam-Errungenschaften": "Steam Achievements",
    "Steam-prestasjoner": "Steam Achievements",
    "Steam-prestaties": "Steam Achievements",
    "Steam-præstationer": "Steam Achievements",
    "Steam-saavutukset": "Steam Achievements",
    "Succès Steam": "Steam Achievements",
    "Достижения Steam": "Steam Achievements",
    "Досягнення Steam": "Steam Achievements",
    "Steam実績": "Steam Achievements",
    "Steam 成就": "Steam Achievements",

    # -------------------------------------------------
    # Steam Trading Cards
    # -------------------------------------------------
    "Cartas Colecionáveis": "Steam Trading Cards",
    "Cartas Colecionáveis Steam": "Steam Trading Cards",
    "Carte collezionabili di Steam": "Steam Trading Cards",
    "Cartes à échanger Steam": "Steam Trading Cards",
    "Cromos de Steam": "Steam Trading Cards",
    "Karty kolekcjonerskie Steam": "Steam Trading Cards",
    "Sběratelské karty": "Steam Trading Cards",
    "Steam-Sammelkarten": "Steam Trading Cards",
    "Steam-byttekort": "Steam Trading Cards",
    "Steam-keräilykortit": "Steam Trading Cards",
    "Steam-ruilkaarten": "Steam Trading Cards",
    "Tarjetas de Steam": "Steam Trading Cards",
    "Колекційні картки Steam": "Steam Trading Cards",
    "Коллекционные карточки Steam": "Steam Trading Cards",
    "Steamトレーディングカード": "Steam Trading Cards",
    "Steam 交換卡片": "Steam Trading Cards",
    "Steam 集换式卡牌": "Steam Trading Cards",

    # -------------------------------------------------
    # Steam Leaderboards
    # -------------------------------------------------
    "Classements Steam": "Steam Leaderboards",
    "Classificações Steam": "Steam Leaderboards",
    "Classifiche di Steam": "Steam Leaderboards",
    "Marcadores de Steam": "Steam Leaderboards",
    "Steam-Bestenlisten": "Steam Leaderboards",
    "Steam-førertavler": "Steam Leaderboards",
    "Tabelas de liderança do Steam": "Steam Leaderboards",
    "Tablas de clasificación de Steam": "Steam Leaderboards",
    "Таблицы лидеров Steam": "Steam Leaderboards",
    "Steamランキング": "Steam Leaderboards",
    "Steam 排行榜": "Steam Leaderboards",

    # -------------------------------------------------
    # Stats
    # -------------------------------------------------
    "Estadísticas": "Stats",
    "Statistik": "Stats",
    "Statystyki": "Stats",
    "Статистика": "Stats",

    # -------------------------------------------------
    # Steam Cloud
    # -------------------------------------------------
    "Nuvem Steam": "Steam Cloud",
    "Steam 云": "Steam Cloud",
    "Steam 雲端": "Steam Cloud",
    "Steamクラウド": "Steam Cloud",

    # -------------------------------------------------
    # Steam Workshop
    # -------------------------------------------------
    "Warsztat Steam": "Steam Workshop",
    "Workshop Steam": "Steam Workshop",
    "Steam-værksted": "Steam Workshop",
    "Мастерская Steam": "Steam Workshop",
    "Steam 创意工坊": "Steam Workshop",
    "Steam 工作坊": "Steam Workshop",

    # -------------------------------------------------
    # Full controller support
    # -------------------------------------------------
    "Compat. contrôleurs complète": "Full controller support",
    "Compat. total c/ comando": "Full controller support",
    "Compat. total com controle": "Full controller support",
    "Compat. total con control": "Full controller support",
    "Compat. total con mando": "Full controller support",
    "Fuld controllerunderstøttelse": "Full controller support",
    "Pełna obsługa kontrolerów": "Full controller support",
    "Plná podpora ovladačů": "Full controller support",
    "Supporto completo per i controller": "Full controller support",
    "Täysi tuki ohjaimille": "Full controller support",
    "Volle Controllerunterstützung": "Full controller support",
    "Volledige controllerondersteuning": "Full controller support",
    "Полная поддержка контроллеров": "Full controller support",
    "Повна підтримка контролерів": "Full controller support",
    "フルコントローラサポート": "Full controller support",
    "完全支持控制器": "Full controller support",
    "完全支援控制器": "Full controller support",

    # -------------------------------------------------
    # Partial Controller Support
    # -------------------------------------------------
    "Compat. contrôleurs partielle": "Partial Controller Support",
    "Compat. parcial com controle": "Partial Controller Support",
    "Compat. parcial con control": "Partial Controller Support",
    "Compat. parcial con mando": "Partial Controller Support",
    "Częściowa obsługa kontrolerów": "Partial Controller Support",
    "Delvis controllerunderstøttelse": "Partial Controller Support",
    "Delvis støtte for kontroller": "Partial Controller Support",
    "Gedeeltelijke controllerondersteuning": "Partial Controller Support",
    "Supporto parziale per i controller": "Partial Controller Support",
    "Teilweise Controllerunterstützung": "Partial Controller Support",
    "Частичная поддержка контроллеров": "Partial Controller Support",
    "部分控制器支援": "Partial Controller Support",
    "部分支持控制器": "Partial Controller Support",
    "部分的コントローラサポート": "Partial Controller Support",

    # -------------------------------------------------
    # In-App Purchases
    # -------------------------------------------------
    "Achats en jeu": "In-App Purchases",
    "Acquisti dall'applicazione": "In-App Purchases",
    "Compras dentro de la aplicación": "In-App Purchases",
    "Compras em aplicativo": "In-App Purchases",
    "Käufe im Spiel": "In-App Purchases",
    "Køb i app": "In-App Purchases",
    "Zakupy w aplikacji": "In-App Purchases",
    "Внутриигровые покупки": "In-App Purchases",
    "アプリ内購入": "In-App Purchases",
    "应用内购买": "In-App Purchases",

    # -------------------------------------------------
    # Online Co-op
    # -------------------------------------------------
    "Online co-op": "Online Co-op",
    "Cooperativo en línea": "Online Co-op",
    "Cooperativos en línea": "Online Co-op",
    "Coopération en ligne": "Online Co-op",
    "Online-Koop": "Online Co-op",
    "Partita cooperativa online": "Online Co-op",
    "Sieciowa kooperacja": "Online Co-op",
    "Verkkoyhteistyöpeli": "Online Co-op",
    "Кооператив (по сети)": "Online Co-op",
    "オンライン協力プレイ": "Online Co-op",
    "在线合作": "Online Co-op",
    "線上合作": "Online Co-op",

    # -------------------------------------------------
    # Online PvP
    # -------------------------------------------------
    "Online-PvP": "Online PvP",
    "PvP online": "Online PvP",
    "JcJ en ligne": "Online PvP",
    "JcJ en línea": "Online PvP",
    "Verkko-PvP": "Online PvP",
    "Игрок против игрока (по сети)": "Online PvP",
    "線上玩家對戰": "Online PvP",
    "线上玩家对战": "Online PvP",

    # -------------------------------------------------
    # PvP
    # -------------------------------------------------
    "JcJ": "PvP",
    "Игрок против игрока": "PvP",
    "玩家对战": "PvP",
    "玩家對戰": "PvP",

    # -------------------------------------------------
    # Co-op
    # -------------------------------------------------
    "Cooperativo": "Co-op",
    "Cooperativos": "Co-op",
    "Coopération": "Co-op",
    "Koop": "Co-op",
    "Kooperacja": "Co-op",
    "Yhteistyöpeli": "Co-op",
    "Кооператив": "Co-op",
    "協力プレイ": "Co-op",
    "合作": "Co-op",

    # -------------------------------------------------
    # Cross-Platform Multiplayer
    # -------------------------------------------------
    "Multijoueur multiplateforme": "Cross-Platform Multiplayer",
    "Multijugador multiplataforma": "Cross-Platform Multiplayer",
    "Plattformübergreifender Mehrspieler": "Cross-Platform Multiplayer",
    "Wieloplatformowa wieloosobowa": "Cross-Platform Multiplayer",
    "Кросс-платформенный мультиплеер": "Cross-Platform Multiplayer",
    "跨平台多人": "Cross-Platform Multiplayer",

    # -------------------------------------------------
    # Game demo
    # -------------------------------------------------
    "Spieldemo": "Game demo",
    "Демоверсия игры": "Game demo",
    "游戏试用版": "Game demo",

    # -------------------------------------------------
    # HDR available
    # -------------------------------------------------
    "HDR disponibili": "HDR available",
    "HDR disponible": "HDR available",
    "可用 HDR": "HDR available"
}

categories["category"] = categories["category"].replace(
    category_mapping
)

print("\nUnique categories after standardization:")
print(sorted(categories["category"].unique()))

print("\nNumber of unique categories after standardization:")
print(categories["category"].nunique())

# =====================================================
# 7. SECOND ROUND STANDARDIZATION
# =====================================================

category_mapping_2 = {

    # Commentary available
    "Comentario disponible": "Commentary available",
    "Поддержка комментариев": "Commentary available",

    # Captions available
    "Legendas disponíveis": "Captions available",
    "Subtítulos disponibles": "Captions available",
    "Tekster tilgængelige": "Captions available",
    "Tekstitys": "Captions available",
    "Поддержка субтитров": "Captions available",
    "支持字幕": "Captions available",

    # VR Support
    "Compatibile con VR": "VR Support",
    "Compatibilidad con RV": "VR Support",
    "Compatible con RV": "VR Support",
    "VR Supported": "VR Support",
    "Поддержка VR": "VR Support",

    # Tracked Controller Support
    "Detección de mov. en mando": "Tracked Controller Support",
    "Supporto per i controller tracciati": "Tracked Controller Support",
    "Поддержка отслеживания контроллеров": "Tracked Controller Support",

    # Shared/Split Screen
    "Geteilter Bildschirm": "Shared/Split Screen",
    "Jaettu näyttö": "Shared/Split Screen",
    "Pantalla dividida/compartida": "Shared/Split Screen",
    "Pantalla partida/compartida": "Shared/Split Screen",
    "Общий/разделённый экран": "Shared/Split Screen",
    "同屏/分屏": "Shared/Split Screen",

    # Shared/Split Screen Co-op
    "Coop locale et écran partagé": "Shared/Split Screen Co-op",
    "Coop. a pantalla (com)partida": "Shared/Split Screen Co-op",
    "Cooperativos en pantalla dividida/compartida": "Shared/Split Screen Co-op",
    "Jaetun näytön yhteistyöpeli": "Shared/Split Screen Co-op",
    "Koop-Spiele mit geteiltem Bildschirm": "Shared/Split Screen Co-op",
    "Кооператив (общий/разделённый экран)": "Shared/Split Screen Co-op",
    "同屏/分屏合作": "Shared/Split Screen Co-op",

    # Shared/Split Screen PvP
    "Jaetun näytön PvP": "Shared/Split Screen PvP",
    "JcJ a pantalla (com)partida": "Shared/Split Screen PvP",
    "JcJ en pantalla dividida/compartida": "Shared/Split Screen PvP",
    "PvP, ecrã partilhado/dividido": "Shared/Split Screen PvP",
    "Игрок против игрока (общий/разделённый экран)": "Shared/Split Screen PvP",

    # LAN Co-op
    "LAN – co-op": "LAN Co-op",
    "Кооператив (локальная сеть)": "LAN Co-op",
    "局域网合作": "LAN Co-op",

    # MMO
    "Multijugador masivo": "MMO",
    "大型多人線上": "MMO",

    # Steam Timeline
    "Oś czasu Steam": "Steam Timeline",
    "Временная шкала Steam": "Steam Timeline",

    # Includes level editor
    "Indeholder baneeditor": "Includes level editor",
    "Sisältää tasoeditorin": "Includes level editor",
    "С редактором уровней": "Includes level editor",
    "包含关卡编辑器": "Includes level editor",

    # Includes Source SDK
    "С инструментами Source SDK": "Includes Source SDK",

    # SteamVR Collectibles
    "Предметы для SteamVR": "SteamVR Collectibles",

    # Valve Anti-Cheat enabled
    "Valve Anti-Cheat integriert": "Valve Anti-Cheat enabled",
    "Valve Anti-Cheat slået til": "Valve Anti-Cheat enabled",
    "Włączona funkcja Anti-Cheat": "Valve Anti-Cheat enabled",
    "Включён античит Valve": "Valve Anti-Cheat enabled",

    # Remote Play Together
    "Remote\xa0Play\xa0Together": "Remote Play Together",
    "远程同乐": "Remote Play Together",

    # Remote Play on TV
    "Remote Play TV:llä": "Remote Play on TV",
    "Remote Play na TV": "Remote Play on TV",
    "Remote Play na telewizorze": "Remote Play on TV",
    "Remote Play op televisies": "Remote Play on TV",
    "Remote Play para TV": "Remote Play on TV",
    "Remote Play sulla TV": "Remote Play on TV",
    "Remote Play sur télévision": "Remote Play on TV",
    "Remote Play на телевизоре": "Remote Play on TV",
    "Remote Play на телевізорі": "Remote Play on TV",
    "Remote\xa0Play en TV": "Remote Play on TV",
    "テレビでRemote Play": "Remote Play on TV",
    "在电视上远程畅玩": "Remote Play on TV",
    "在電視上遠端暢玩": "Remote Play on TV",

    # Remote Play on Phone
    "Remote Play auf Smartphones": "Remote Play on Phone",
    "Remote Play na telefonie": "Remote Play on Phone",
    "Remote Play no celular": "Remote Play on Phone",
    "Remote Play op telefoons": "Remote Play on Phone",
    "Remote Play para móviles": "Remote Play on Phone",
    "Remote Play sul telefono": "Remote Play on Phone",
    "Remote Play sur téléphone": "Remote Play on Phone",
    "Remote Play на телефоне": "Remote Play on Phone",
    "Remote\xa0Play en móvil": "Remote Play on Phone",
    "在手机上远程畅玩": "Remote Play on Phone",

    # Remote Play on Tablet
    "Remote Play auf Tablets": "Remote Play on Tablet",
    "Remote Play na tablecie": "Remote Play on Tablet",
    "Remote Play no tablet": "Remote Play on Tablet",
    "Remote Play op tablets": "Remote Play on Tablet",
    "Remote Play para tabletas": "Remote Play on Tablet",
    "Remote Play sul tablet": "Remote Play on Tablet",
    "Remote Play sur tablette": "Remote Play on Tablet",
    "Remote Play tabletilla": "Remote Play on Tablet",
    "Remote Play на планшете": "Remote Play on Tablet",
    "Remote\xa0Play en tableta": "Remote Play on Tablet",
    "在平板上远程畅玩": "Remote Play on Tablet"
}

categories["category"] = categories["category"].replace(
    category_mapping_2
)

print("\nUnique categories after second standardization:")
print(sorted(categories["category"].unique()))

print("\nNumber of unique categories after second standardization:")
print(categories["category"].nunique())

# =====================================================
# 8. REMOVE DUPLICATES AFTER STANDARDIZATION
# =====================================================

categories = categories.drop_duplicates(
    subset=["app_id", "category"]
)

categories = categories.reset_index(drop=True)


# =====================================================
# 9. FINAL VALIDATION
# =====================================================

print("\n----- FINAL VALIDATION -----")

print("\nFinal shape:")
print(categories.shape)

print("\nMissing values:")
print(categories.isnull().sum())

print("\nDuplicate rows:")
print(categories.duplicated().sum())

print("\nNumber of unique categories:")
print(categories["category"].nunique())

print("\nFinal unique categories:")
print(sorted(categories["category"].unique()))


# =====================================================
# 10. CLEANING SUMMARY
# =====================================================

print("\n----- CLEANING SUMMARY -----")

print("Original rows:", original_rows)
print("Final rows:", len(categories))
print("Rows removed:", original_rows - len(categories))


# =====================================================
# 11. EXPORT CLEANED DATA
# =====================================================

categories.to_csv("data/processed/categories_cleaned.csv", index=False)

print("\nCategories data cleaning completed successfully.")

#Conclusion:
#The categories dataset initially contained 315 unique labels across multiple 
#languages and naming conventions. After standardization, these were consolidated 
#into 42 consistent English categories. 
#This process created duplicate app_id–category combinations, 
#resulting in the removal of 79 redundant rows.

#=======================================================
# 12. Top 5
#=======================================================

top5_categories = categories["category"].value_counts().head(5)

print("\nTop 5 Categories:")
print(top5_categories)

total_games = categories["app_id"].nunique()

top5_game_share = (
    categories.groupby("category")["app_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(5)
)

top5_game_share_pct = top5_game_share / total_games * 100

print("\nTop 5 Categories by Number of Games:")
print(top5_game_share)

print("\nPercentage of Games:")
print(top5_game_share_pct)

#Top 5 Categories:
#Category                   Amount     Percent(%)
#Single-player              125418     93.321825
#Family Sharing              75923     56.493270
#Steam Achievements          54651     40.665064
#Full controller support     33009     24.561547
#Steam Cloud                 28792     21.423735


'''
Role: You are a Data Engineer with strong Python/Pandas expertise, merging three long-format CSVs into one wide-format dataset on app_id.
Context: Three files — tags.csv, categories.csv, genres.csv — each long-format (one row per app_id + value pair, e.g. tags.csv has app_id and tag).
Objective: Produce categories_tags_genres_merged.csv: one row per app_id, with categories, tags, and genres each collapsed into a single comma-separated string column. No app_id should be lost, and no value invented.
Tasks:

Load all three files; report shape and unique app_id count for each (confirming each file truly has one row per app_id before merging).
Outer-merge all three on app_id, so every app_id present in any file is kept. An app_id missing from one source gets a real NaN there, not a fabricated value or empty string.
Validate: no duplicate app_ids, row count equals the true union of app_ids across the three files, no rows dropped.
Save as categories_tags_genres_merged.csv and report row count plus how many app_ids came from each source.
Constraints (Do Not):

Do not drop any app_id, even if it only appears in one source file.
Do not fabricate values for missing app_ids.
Do not overwrite the original CSVs.
'''

import pandas as pd

# ---------------------------------------------------------------------------
# 1. LOAD + VERIFY (each file already collapsed to one row per app_id)
# ---------------------------------------------------------------------------
tags = pd.read_csv("data/processed/tags_cleaned.csv")
categories = pd.read_csv("data/processed/categories_cleaned.csv")
genres = pd.read_csv("data/processed/genres_cleaned.csv")

for name, df in [("tags", tags), ("categories", categories), ("genres", genres)]:
    dup_count = df["app_id"].duplicated().sum()
    print(f"{name}: shape={df.shape}  unique app_ids={df['app_id'].nunique()}  duplicate app_ids={dup_count}")
    assert dup_count == 0, f"{name}.csv has duplicate app_ids -- expected one row per app_id"

# ---------------------------------------------------------------------------
# 2. OUTER MERGE ON app_id -- no app_id lost, missing values stay real NaN
# ---------------------------------------------------------------------------
merged = tags.merge(categories, on="app_id", how="outer").merge(genres, on="app_id", how="outer")

# ---------------------------------------------------------------------------
# 3. VALIDATE
# ---------------------------------------------------------------------------
all_ids = set(tags["app_id"]) | set(categories["app_id"]) | set(genres["app_id"])
print("\nmerged shape:", merged.shape)
print("duplicate app_ids in merged:", merged["app_id"].duplicated().sum())
print("row count matches true union of app_ids:", len(merged) == len(all_ids))

for name, df in [("tags", tags), ("categories", categories), ("genres", genres)]:
    missing = len(all_ids - set(df["app_id"]))
    print(f"app_ids missing from {name}.csv (present in union but not here): {missing}")

# ---------------------------------------------------------------------------
# 4. SAVE
# ---------------------------------------------------------------------------
merged.to_csv("data/processed/categories_tags_genres_merged.csv", index=False)
print(f"\nSaved: data/processed/categories_tags_genres_merged.csv  shape={merged.shape}")
