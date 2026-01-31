import os
import pandas as pd

IN_API = "data/processed/api_football/fixtures_processed.csv"
OUT_DIR = "data/curated"
OUT_FILE = os.path.join(OUT_DIR, "api_matches_curated.csv")

MAP_PATH = "data/processed/mappings/api_to_kaggle_mapping.csv"

os.makedirs(OUT_DIR, exist_ok=True)

def normalize(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.replace(r"\s+", " ", regex=True)

def load_map(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        m = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        m = pd.read_csv(path, encoding="cp1252")
    m["api_name"] = normalize(m["api_name"])
    m["kaggle_name"] = normalize(m["kaggle_name"])
    return dict(zip(m["api_name"], m["kaggle_name"]))

df = pd.read_csv(IN_API, parse_dates=["date"])

# Normalizar nombres
df["home_team"] = normalize(df["home_team"])
df["away_team"] = normalize(df["away_team"])

# Aplicar mapping API -> Kaggle (solo si lo creaste)
mp = load_map(MAP_PATH)
if mp:
    df["home_team"] = df["home_team"].replace(mp)
    df["away_team"] = df["away_team"].replace(mp)
    print(f"Mapping API->Kaggle aplicado: {len(mp)} reglas")
else:
    print("No hay mapping API->Kaggle. (OK, pero bajará el match con ranking)")

# Construir output con esquema compatible con Kaggle curado
out = pd.DataFrame({
    "date": df["date"],
    "home_team": df["home_team"],
    "away_team": df["away_team"],
    "home_score": df["home_score"],
    "away_score": df["away_score"],
    "tournament": df.get("tournament", pd.NA),
    "city": pd.NA,
    "country": pd.NA,
    "neutral": pd.NA,

    # columnas del curado Kaggle (aquí API no las trae)
    "has_shootout": False,
    "shootout_winner": pd.NA,
    "goalscorers_rows": 0,
    "penalty_goals_count": 0,
    "own_goals_count": 0,

    # trazabilidad
    "fixture_id": df["fixture_id"],
    "league_id": df["league_id"],
    "season": df["season"],
    "source": "api_football"
})

out.to_csv(OUT_FILE, index=False, encoding="utf-8")
print("OK ->", OUT_FILE, "| filas:", len(out))
print(out.head(5))
