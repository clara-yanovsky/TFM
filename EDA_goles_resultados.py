import os
from pathlib import Path
import logging
import numpy as np
import pandas as pd

# configuración de rutas
INPUT_PATH = "matches_final_curated.csv"
OUTPUT_DIR = "analisis_exploratoria_inicial.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)
#carga de datos
df = pd.read_csv(INPUT_PATH)
# Vista general rápida del DataFrame
print("Tamaño:", df.shape)
print("Columnas:", df.columns.tolist())
#conversión de tipos y limpieza minima
#date -> datetime; valores vacios quedaran como NaT
df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
#neutral: viene como "0"/"1" o similar -> bool
def to_bool_from_01(x):
    try:
        return bool(int(x))
    except Exception:
        #Si viene como ya booleano o string "true"/"false"
        if str(x).lower() in ["true", "t", "verdadero", "yes", "y"]:
            return True
        if str(x).lower() in ["false", "f", "falso", "no", "n", "nan", "none", ""]:
            return False
        return False

df["neutral"] = df["neutral"].apply(to_bool_from_01)
#has_shootout: convertir a bool
def to_bool_generic(x):
    if pd.isna(x):
        return False
    s = str(x).strip().lower()
    if s in ["true", "t", "1", "yes", "y", "verdadero"]:
        return True
    if s in ["false", "f", "0", "no", "n", "falso", "nan", "none", ""]:
        return False
    return False

df["has_shootout"] = df["has_shootout"].apply(to_bool_generic)
#Marcadores a enteros (si vienen como texto)
for c in["home__score", "away_score", "goalscorers_rows", "penalty_goals_count", "own_goals_count"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
#Ranking (si existen, convertir a numérico)
for c in ["home_rank_position", "home_rank_points", "away_rank_position", "away_rank_points", "rank_points_diff"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
#Columnas derivadas para el EDA
df.columns = df.columns.str.strip().str.lower()
df["total_goals"] = df["home_score"].astype(float) + df["away_score"].astype(float)
df["goal_diff_home"] = df["home_score"].astype(float) - df["away_score"].astype(float)
#resultado (texto) a partir de match_outcome si existe: si no, se infiere por el marcador
def outcome_label(row):
    if "match_outcome" in row.index and pd.notna(row["match_outcome"]):
        if row["match_outcome"] == 1:
            return "home_win"
        elif row["match_outcome"] == 0:
            return "draw"
        elif row["match_outcome"] == -1:
            return "away_win"
    #fallback por marcador
    hs, as_= row["home_score"], row["away_score"]
    if pd.isna(hs) or pd.isna(as_):
        return np.nan
    if hs > as_:
        return "home_win"
    if hs < as_:
        return "away_win"
    return "draw"

df["result_label"] = df.apply(outcome_label, axis=1)

#Normalización de nombres de selecciones (user columnas *_norm se existen)
df["home_team_std"] = df["home_team_norm"] if "home_team_norm" in df.columns else df["home_team"]
df["away_team_std"] = df["away_team_norm"] if "away_team_norm" in df.columns else df["away_team"]

#guardado opcional del dataset preparado
df.to_csv(os.path.join(OUTPUT_DIR, "matches_prepared.csv"), index=False)
print("Archivo preparado guardado en outputs/matched_prepared.csv")


### Análisis 1: Distribución de goles y resultados
import seaborn as sns
import matplotlib.pyplot as plt

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#Estadisticos descriptivos de goles
desc_cols = ["home_score", "away_score", "total_goals"]
print(df[desc_cols].describe())
#histogramas de goles
sns.set(style="whitegrid")
fig, axes = plt.subplot(1,3, figsize=(18,5))
sns.histplot(df["home_score"], kde=False, bins=range(0, int(df["home_score"].max()+2)), ax=axes[0], color="#1f77b4")
axes[0].set_title("Distribución - Goles del local")
axes[0].set_xlabel("Goles local")

sns.histplot(df["away_score"], kde=False, bins=range(0, int(df["away_score"].max()+2)), ax=axes[1], color="#ff7f0e")
axes[1].set_title("Distribución - Goles del visitante")
axes[1].set_xlabel("Goles visitante")

sns.histplot(df["total_goals"], kde=False, bins=range(0, int(df["total_goals"].max()+2)), ax=axes[2], color="#2ca02c")
axes[2].set_title("Distribución - Goles totales")
axes[2].set_xlabel("Goles totales")

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "distribucion_goles.png"), dpi=200)
plt.close()

#proporción de resultados (home_win/draw/away_win)
result_share = df["result_label"].value_counts(normalize=True).rename("proporcion").reset_index().rename(columns={"index": "resultado"})
print(result_share)

sns.barplot(data=result_share, x="resultado", y="proporcion", palette="viridis")
plt.title("proporción de resultados")
plt.ylabel("Proporción")
plt.xlabel("")
plt.savefig(os.path.join(OUTPUT_DIR, "proporcion_resultados.png"), dpi=200, bbox_inches="tight")
plt.close()

#Marcadores más frecuentes(scorelines)
df["scoreline"] = df["home_score"].astype(str) + "-" + df["away_score"].astype(str)
top_scorelines = df["scoreline"].value_counts().head(15).reset_index()
top_scorelines.columns = ["scoreline", "frecuencia"]
print(top_scorelines)
sns.barplot(data=top_scorelines, x="scoreline", y="frecuencia", palette="mako")
plt.title("Top 15 Marcadores más frecuentes")
plt.ylabel("Frecuencia")
plt.xlabel("Marcador")
plt.savefig(os.path.join(OUTPUT_DIR, "top_scorelines.png"), dpi=200, bbox_inches="tight")
plt.close()

#ventaja de localia (winrate del local general y por 'Neutral')
home_win_rate_global = (df["result_label"] == "home_win").mean()
print("Tasa de victoria del local (global):", round(home_win_rate_global,3))

if"neutral" in df.columns:
    by_neutral = df.groupby("neutral")["result_label"].apply(lambda s:(s=="home_win").mean())
    print("Tasa de victoria del local por neutralidad:\n", by_neutral)
    by_neutral.to_csv(os.path.join(OUTPUT_DIR, "home_winrate_por_neutral.csv"))

#exportes utiles
result_share.to_csv(os.path.join(OUTPUT_DIR, "proporcion_resultados.csv"), index=False)
top_scorelines.to_csv(os.path.join(OUTPUT_DIR, "top_scorelines.csv"), index=False)
