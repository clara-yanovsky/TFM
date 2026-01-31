import os
import json
import glob
import pandas as pd

RAW_GLOB = "data/raw/api_football/fixtures/**/fixtures_*.json"
OUT_DIR = "data/processed/api_football"
OUT_FILE = os.path.join(OUT_DIR, "fixtures_processed.csv")

os.makedirs(OUT_DIR, exist_ok=True)

rows = []
files = glob.glob(RAW_GLOB, recursive=True)

print("Archivos RAW encontrados:", len(files))

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for m in data.get("response", []):
        rows.append({
            "fixture_id": m["fixture"]["id"],
            # ISO: YYYY-MM-DD
            "date": m["fixture"]["date"][:10],
            "home_team": m["teams"]["home"]["name"],
            "away_team": m["teams"]["away"]["name"],
            # usar "goals" de la API como score final
            "home_score": m["goals"]["home"],
            "away_score": m["goals"]["away"],
            "tournament": m["league"]["name"],
            "league_id": m["league"]["id"],
            "season": m["league"]["season"],
            "source": "api_football"
        })

df = pd.DataFrame(rows)

# Convertir date a datetime (para joins/orden)
df["date"] = pd.to_datetime(df["date"], errors="coerce")

df.to_csv(OUT_FILE, index=False, encoding="utf-8")
print("OK ->", OUT_FILE, "| filas:", len(df))
print(df.head(5))
