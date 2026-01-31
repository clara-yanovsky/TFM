import os
import pandas as pd


IN_RESULTS = "data/processed/kaggle/results_processed.csv"
IN_SHOOTOUTS = "data/processed/kaggle/shootouts_processed.csv"
IN_GOALSCORERS = "data/processed/kaggle/goalscorers_processed.csv"

OUT_DIR = "data/curated"
OUT_FILE = os.path.join(OUT_DIR, "kaggle_matches_curated.csv")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # -------------------------
    # 1) Cargar RESULTS (base)
    # -------------------------
    df_results = pd.read_csv(IN_RESULTS, parse_dates=["date"])
    for c in ["home_team", "away_team"]:
        df_results[c] = df_results[c].astype(str).str.strip()

    base_n = len(df_results)
    print("Results base:", base_n)

    # Llave estándar del partido
    key_cols = ["date", "home_team", "away_team"]

    # --------------------------------
    # 2) JOIN con SHOOTOUTS (penales)
    # --------------------------------
    df_shoot = pd.read_csv(IN_SHOOTOUTS, parse_dates=["date"])
    for c in ["home_team", "away_team", "winner"]:
        if c in df_shoot.columns:
            df_shoot[c] = df_shoot[c].astype(str).str.strip()

    # Dejar solo columnas necesarias
    keep_shoot = key_cols + (["winner"] if "winner" in df_shoot.columns else [])
    df_shoot = df_shoot[keep_shoot].copy()

    # Evitar duplicados accidentales
    df_shoot = df_shoot.drop_duplicates(subset=key_cols)

    df = df_results.merge(df_shoot, on=key_cols, how="left")

    # Crear columnas útiles
    df = df.rename(columns={"winner": "shootout_winner"})
    df["has_shootout"] = df["shootout_winner"].notna()

    print("Shootouts total:", len(df_shoot))
    print("Matches con shootout (después del join):", int(df["has_shootout"].sum()))

    # Detectar shootouts que no hicieron match con results
    df_results_keys = df_results[key_cols].drop_duplicates()
    df_shoot_keys = df_shoot[key_cols].drop_duplicates()

    missing_shoot = df_shoot_keys.merge(df_results_keys, on=key_cols, how="left", indicator=True)
    missing_shoot = missing_shoot[missing_shoot["_merge"] == "left_only"]

    print("\nShootouts sin match en results:", len(missing_shoot))
    print(missing_shoot.head(20))

    # ---------------------------------------------------
    # 3) Integrar GOALSCORERS agregando a nivel partido
    # ---------------------------------------------------
    df_goals = pd.read_csv(IN_GOALSCORERS, parse_dates=["date"])
    for c in ["home_team", "away_team", "team", "scorer"]:
        if c in df_goals.columns:
            df_goals[c] = df_goals[c].astype(str).str.strip()

    # Normalizar flags si vienen como strings
    for flag in ["penalty", "own_goal"]:
        if flag in df_goals.columns:
            # puede venir como True/False o 'True'/'False'
            df_goals[flag] = df_goals[flag].astype(str).str.lower().isin(["true", "1", "yes"])

    # Agregados por partido: conteo total de goles registrados, penales, autogoles
    agg = {"scorer": "count"}
    if "penalty" in df_goals.columns:
        agg["penalty"] = "sum"
    if "own_goal" in df_goals.columns:
        agg["own_goal"] = "sum"

    df_goals_agg = (
        df_goals
        .groupby(key_cols, as_index=False)
        .agg(agg)
        .rename(columns={
            "scorer": "goalscorers_rows",
            "penalty": "penalty_goals_count" if "penalty" in agg else "penalty_goals_count",
            "own_goal": "own_goals_count" if "own_goal" in agg else "own_goals_count",
        })
    )

    # Si no existían columnas en origen, aseguramos que existan con 0
    if "penalty_goals_count" not in df_goals_agg.columns:
        df_goals_agg["penalty_goals_count"] = 0
    if "own_goals_count" not in df_goals_agg.columns:
        df_goals_agg["own_goals_count"] = 0

    df = df.merge(df_goals_agg, on=key_cols, how="left")

    # Rellenar NaN de agregados con 0 (partidos sin registros de goleadores)
    for c in ["goalscorers_rows", "penalty_goals_count", "own_goals_count"]:
        df[c] = df[c].fillna(0).astype(int)

    print("Partidos con alguna fila en goalscorers:", int((df["goalscorers_rows"] > 0).sum()))

    # -------------------------
    # 4) Validaciones rápidas
    # -------------------------
    print("\n=== VALIDACIONES ===")
    print("Total filas final (debe ser igual a results):", len(df), "| base:", base_n)

    # comprobar duplicados por llave
    dup = df.duplicated(subset=key_cols).sum()
    print("Duplicados por llave (date,home,away):", int(dup))
    dups_df = df[df.duplicated(subset=key_cols, keep=False)].sort_values(key_cols)
    print("\nDuplicados (muestra completa):")
    print(dups_df[key_cols + ["tournament", "city", "country", "home_score", "away_score"]].head(50))
    df["match_key"] = (
    df["date"].dt.strftime("%Y-%m-%d") + "|" +
    df["home_team"].astype(str) + "|" +
    df["away_team"].astype(str) + "|" +
    df.index.astype(str)
    )

    # -------------------------
    # 5) Guardar CURATED
    # -------------------------
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print("\nCURATED guardado en:", OUT_FILE)

if __name__ == "__main__":
    main()

