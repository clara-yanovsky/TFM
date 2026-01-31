import os
import pandas as pd

RAW_DIR = "data/raw/kaggle"
OUT_DIR = "data/processed/kaggle"

os.makedirs(OUT_DIR, exist_ok=True)

def load_raw_csv(basename: str) -> pd.DataFrame:
    """
    Carga un CSV desde RAW con nombre exacto (sin o con .csv).
    Soporta que en Windows a veces se vea como 'results' pero realmente sea 'results.csv'.
    """
    p1 = os.path.join(RAW_DIR, f"{basename}.csv")
    p2 = os.path.join(RAW_DIR, basename)

    if os.path.exists(p1):
        return pd.read_csv(p1)
    if os.path.exists(p2):
        return pd.read_csv(p2)

    raise FileNotFoundError(f"No encontré {basename}.csv ni {basename} dentro de {RAW_DIR}")


def save_processed(df: pd.DataFrame, out_name: str):
    out_path = os.path.join(OUT_DIR, out_name)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"OK -> {out_name} | filas={len(df)}")


# =========================
# 1) RESULTS (partidos)
# =========================
df_results = load_raw_csv("results")

# Fecha
if "date" in df_results.columns:
    df_results["date"] = pd.to_datetime(df_results["date"], errors="coerce")

# Strings comunes
for c in ["home_team", "away_team", "tournament", "city", "country", "neutral"]:
    if c in df_results.columns:
        df_results[c] = df_results[c].astype(str).str.strip()

save_processed(df_results, "results_processed.csv")


# =========================
# 2) SHOOTOUTS (penales)
# =========================
df_shoot = load_raw_csv("shootouts")

if "date" in df_shoot.columns:
    df_shoot["date"] = pd.to_datetime(df_shoot["date"], errors="coerce")

for c in ["home_team", "away_team", "winner"]:
    if c in df_shoot.columns:
        df_shoot[c] = df_shoot[c].astype(str).str.strip()

save_processed(df_shoot, "shootouts_processed.csv")


# =========================
# 3) GOALSCORERS (goles individuales)
# =========================
df_goals = load_raw_csv("goalscorers")

if "date" in df_goals.columns:
    df_goals["date"] = pd.to_datetime(df_goals["date"], errors="coerce")

for c in ["home_team", "away_team", "team", "scorer", "minute", "own_goal", "penalty"]:
    if c in df_goals.columns:
        df_goals[c] = df_goals[c].astype(str).str.strip()

save_processed(df_goals, "goalscorers_processed.csv")


# =========================
# 4) FORMER_NAMES (nombres históricos)
# =========================
df_names = load_raw_csv("former_names")

# Fechas (el dataset a veces usa 'from' y 'to')
for col in ["from", "to", "start_date", "end_date"]:
    if col in df_names.columns:
        df_names[col] = pd.to_datetime(df_names[col], errors="coerce")

for c in df_names.columns:
    if df_names[c].dtype == "object":
        df_names[c] = df_names[c].astype(str).str.strip()

save_processed(df_names, "former_names_processed.csv")
