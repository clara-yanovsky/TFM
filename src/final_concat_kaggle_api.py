import os
import pandas as pd

OUT_DIR = "data/curated"
OUT_FILE = os.path.join(OUT_DIR, "matches_final_curated.csv")

os.makedirs(OUT_DIR, exist_ok=True)

k = pd.read_csv("data/curated/kaggle_matches_with_ranking.csv", parse_dates=["date"])
a = pd.read_csv("data/curated/api_matches_with_ranking.csv", parse_dates=["date"])

# Asegurar columna source
if "source" not in k.columns:
    k["source"] = "kaggle"
if "source" not in a.columns:
    a["source"] = "api_football"

final = pd.concat([k, a], ignore_index=True)

final.to_csv(OUT_FILE, index=False, encoding="utf-8")
print("OK ->", OUT_FILE, "| filas:", len(final))
print(final["source"].value_counts())
print("Rango fechas:", final["date"].min(), "->", final["date"].max())
