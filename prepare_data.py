import pandas as pd
import json
import os

# Cesty k souborům
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_path = os.path.join(BASE_DIR, "tmdb_5000_movies.csv")
credits_path = os.path.join(BASE_DIR, "tmdb_5000_credits.csv")
output_dir = os.path.join(BASE_DIR, "clean_data")
os.makedirs(output_dir, exist_ok=True)

# Načtení dat
print("Načítám data...")
movies_raw = pd.read_csv(movies_path)
credits_raw = pd.read_csv(credits_path)

# ============================================================
# 1. MOVIES - hlavní tabulka (čistá, bez JSON sloupců)
# ============================================================
print("Připravuji tabulku Movies...")

movies = movies_raw[["id", "title", "original_language", "release_date", "budget", "revenue", "runtime", "vote_average", "vote_count", "popularity", "status"]].copy()

# Odstranit čárky z názvu filmu (aby nerozbíjely CSV)
movies["title"] = movies["title"].str.replace(",", " -", regex=False)

# Vyčistit datumy
movies["release_date"] = pd.to_datetime(movies["release_date"], errors="coerce")
movies["release_year"] = movies["release_date"].dt.year.astype("Int64")
movies["release_month"] = movies["release_date"].dt.month.astype("Int64")

# Dekáda pro hierarchii
movies["decade"] = (movies["release_year"] // 10 * 10).astype("Int64")

# Profit a ROI jako kalkulované sloupce (předpřipravené)
movies["profit"] = movies["revenue"] - movies["budget"]

# Filtrovat filmy bez data nebo s nulovým rozpočtem i tržbami
movies = movies[movies["release_date"].notna()].copy()

# Nahradit None/NaN za 0 aby Power BI správně rozpoznal čísla
numeric_cols = ["budget", "revenue", "runtime", "vote_count"]
for col in numeric_cols:
    movies[col] = pd.to_numeric(movies[col], errors="coerce").fillna(0).astype(int)

# Desetinná čísla - zaokrouhlit aby nebyly problémy s tečkou/čárkou
movies["vote_average"] = pd.to_numeric(movies["vote_average"], errors="coerce").fillna(0)
movies["popularity"] = pd.to_numeric(movies["popularity"], errors="coerce").fillna(0)

movies["profit"] = movies["revenue"] - movies["budget"]

print(f"  {len(movies)} filmu")

# ============================================================
# 2. GENRES - žánry (bridge tabulka movie_id -> genre)
# ============================================================
print("Připravuji tabulku Genres...")

genres_rows = []
for _, row in movies_raw.iterrows():
    try:
        genres = json.loads(row["genres"].replace("'", '"'))
        for g in genres:
            genres_rows.append({"movie_id": row["id"], "genre_id": g["id"], "genre_name": g["name"]})
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

genres_bridge = pd.DataFrame(genres_rows)

# Dimenzní tabulka žánrů
genres_dim = genres_bridge[["genre_id", "genre_name"]].drop_duplicates().sort_values("genre_name").reset_index(drop=True)

# Bridge tabulka (jen movie_id + genre_id)
genres_bridge_clean = genres_bridge[["movie_id", "genre_id"]].drop_duplicates()

print(f"{len(genres_dim)} žánrů, {len(genres_bridge_clean)} propojení")

# ============================================================
# 3. CAST - herci (top 10 per film pro rozumnou velikost)
# ============================================================
print("Připravuji tabulku Cast...")

cast_rows = []
for _, row in credits_raw.iterrows():
    try:
        cast = json.loads(row["cast"].replace("'", '"'))
        for i, person in enumerate(cast[:10]):  # Top 10 herců na film
            cast_rows.append({
                "movie_id": row["movie_id"],
                "actor_id": person["id"],
                "actor_name": person["name"],
                "character": person.get("character", ""),
                "gender": person.get("gender", 0),
                "cast_order": i + 1
            })
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

cast_bridge = pd.DataFrame(cast_rows)

# Dimenzní tabulka herců
actors_dim = cast_bridge[["actor_id", "actor_name", "gender"]].drop_duplicates(subset=["actor_id"]).sort_values("actor_name").reset_index(drop=True)
actors_dim["gender_label"] = actors_dim["gender"].map({0: "Unknown", 1: "Female", 2: "Male"})

# Bridge tabulka
cast_bridge_clean = cast_bridge[["movie_id", "actor_id", "character", "cast_order"]].drop_duplicates()

print(f"{len(actors_dim)} herců, {len(cast_bridge_clean)} rolí")

# ============================================================
# 4. DIRECTORS - režiséři (z crew kde job = Director)
# ============================================================
print("Připravuji tabulku Directors...")

directors_rows = []
for _, row in credits_raw.iterrows():
    try:
        crew = json.loads(row["crew"].replace("'", '"'))
        for person in crew:
            if person.get("job") == "Director":
                directors_rows.append({
                    "movie_id": row["movie_id"],
                    "director_id": person["id"],
                    "director_name": person["name"],
                    "gender": person.get("gender", 0)
                })
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

directors_bridge = pd.DataFrame(directors_rows)

# Dimenzní tabulka režisérů
directors_dim = directors_bridge[["director_id", "director_name", "gender"]].drop_duplicates(subset=["director_id"]).sort_values("director_name").reset_index(drop=True)
directors_dim["gender_label"] = directors_dim["gender"].map({0: "Unknown", 1: "Female", 2: "Male"})

# Bridge tabulka
directors_bridge_clean = directors_bridge[["movie_id", "director_id"]].drop_duplicates()

print(f"{len(directors_dim)} režisérů, {len(directors_bridge_clean)} propojení")

# ============================================================
# 5. PRODUCTION COMPANIES
# ============================================================
print("Připravuji tabulku Production Companies...")

companies_rows = []
for _, row in movies_raw.iterrows():
    try:
        companies = json.loads(row["production_companies"].replace("'", '"'))
        for c in companies:
            companies_rows.append({
                "movie_id": row["id"],
                "company_id": c["id"],
                "company_name": c["name"]
            })
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

companies_bridge = pd.DataFrame(companies_rows)

# Dimenzní tabulka
companies_dim = companies_bridge[["company_id", "company_name"]].drop_duplicates(subset=["company_id"]).sort_values("company_name").reset_index(drop=True)

# Bridge tabulka
companies_bridge_clean = companies_bridge[["movie_id", "company_id"]].drop_duplicates()

print(f"{len(companies_dim)} společností, {len(companies_bridge_clean)} propojení")

# ============================================================
# 6. COUNTRIES - produkční země
# ============================================================
print("Připravuji tabulku Countries...")

countries_rows = []
for _, row in movies_raw.iterrows():
    try:
        countries = json.loads(row["production_countries"].replace("'", '"'))
        for c in countries:
            countries_rows.append({
                "movie_id": row["id"],
                "country_code": c["iso_3166_1"],
                "country_name": c["name"]
            })
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

countries_bridge = pd.DataFrame(countries_rows)
countries_dim = countries_bridge[["country_code", "country_name"]].drop_duplicates(subset=["country_code"]).sort_values("country_name").reset_index(drop=True)
countries_bridge_clean = countries_bridge[["movie_id", "country_code"]].drop_duplicates()

print(f"{len(countries_dim)} zemí, {len(countries_bridge_clean)} propojení")

# ============================================================
# 7. CALENDAR - kalendářní tabulka pro časovou hierarchii
# ============================================================
print("Připravuji kalendářní tabulku...")

min_year = int(movies["release_year"].min())
max_year = int(movies["release_year"].max())

dates = pd.date_range(start=f"{min_year}-01-01", end=f"{max_year}-12-31", freq="D")
calendar = pd.DataFrame({"date": dates})
calendar["year"] = calendar["date"].dt.year
calendar["month"] = calendar["date"].dt.month
calendar["month_name"] = calendar["date"].dt.strftime("%B")
calendar["quarter"] = calendar["date"].dt.quarter
calendar["quarter_label"] = "Q" + calendar["quarter"].astype(str)
calendar["decade"] = (calendar["year"] // 10 * 10)
calendar["decade_label"] = calendar["decade"].astype(str) + "s"

print(f"{len(calendar)} dní ({min_year}-{max_year})")

# ============================================================
# EXPORT do CSV
# ============================================================
print("\nExportuji CSV soubory...")

csv_params = {"index": False, "encoding": "utf-8-sig"}

# Movies jako TSV (tabulátor) - žádné problémy s čárkami v textu
movies.to_csv(os.path.join(output_dir, "movies.txt"), index=False, encoding="utf-8-sig", sep="\t")
genres_dim.to_csv(os.path.join(output_dir, "genres.csv"), **csv_params)
genres_bridge_clean.to_csv(os.path.join(output_dir, "movies_genres.csv"), **csv_params)
actors_dim.to_csv(os.path.join(output_dir, "actors.csv"), **csv_params)
cast_bridge_clean.to_csv(os.path.join(output_dir, "movies_cast.csv"), **csv_params)
directors_dim.to_csv(os.path.join(output_dir, "directors.csv"), **csv_params)
directors_bridge_clean.to_csv(os.path.join(output_dir, "movies_directors.csv"), **csv_params)
companies_dim.to_csv(os.path.join(output_dir, "companies.csv"), **csv_params)
companies_bridge_clean.to_csv(os.path.join(output_dir, "movies_companies.csv"), **csv_params)
countries_dim.to_csv(os.path.join(output_dir, "countries.csv"), **csv_params)
countries_bridge_clean.to_csv(os.path.join(output_dir, "movies_countries.csv"), **csv_params)
calendar.to_csv(os.path.join(output_dir, "calendar.csv"), **csv_params)

print("\n[OK] Hotovo! Vytvořené soubory:")
for f in sorted(os.listdir(output_dir)):
    size = os.path.getsize(os.path.join(output_dir, f)) / 1024
    print(f"   {f} ({size:.0f} KB)")

print(f"\n Výstupní složka: {output_dir}")
print("""
===================================================
  PROPOJENÍ TABULEK V POWER BI (vazby/relationships):
===================================================
  movies.id        movies_genres.movie_id
  genres.genre_id  movies_genres.genre_id
  movies.id        movies_cast.movie_id
  actors.actor_id  movies_cast.actor_id
  movies.id        movies_directors.movie_id
  directors.director_id -> movies_directors.director_id
  movies.id        movies_companies.movie_id
  companies.company_id -> movies_companies.company_id
  movies.id        movies_countries.movie_id
  countries.country_code -> movies_countries.country_code
  calendar.date    movies.release_date

  HIERARCHIE:
  Dekáda -> Rok -> Měsíc (v calendar tabulce)
  Žánr -> Film (přes genres bridge)
===================================================
""")
