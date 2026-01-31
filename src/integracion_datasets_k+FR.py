import os
import pandas as pd


IN_MATCHES = "data/curated/kaggle_matches_curated.csv"
IN_RANKING = "data/processed/football_ranking/ranking_processed.csv"
IN_MAPPING = "data/processed/mappings/team_name_mapping.csv"

OUT_DIR = "data/curated"
OUT_FILE = os.path.join(OUT_DIR, "kaggle_matches_with_ranking.csv")


def normalize_team_name(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.encode("latin1", errors="ignore")
        .str.decode("utf-8", errors="ignore")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


def load_mapping(path: str) -> dict:
    if not os.path.exists(path):
        return {}

    # Intentar UTF-8 primero; si falla, usar cp1252 (Windows)
    try:
        m = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        m = pd.read_csv(path, encoding="cp1252")

    # Validación mínima de columnas
    required = {"kaggle_name", "ranking_name"}
    if not required.issubset(set(m.columns)):
        raise ValueError(f"El mapping debe tener columnas {required}. Columnas encontradas: {list(m.columns)}")

    m["kaggle_name"] = normalize_team_name(m["kaggle_name"])
    m["ranking_name"] = normalize_team_name(m["ranking_name"])
    return dict(zip(m["kaggle_name"], m["ranking_name"]))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) Cargar
    df = pd.read_csv(IN_MATCHES, parse_dates=["date"])
    rank = pd.read_csv(IN_RANKING)

    # 2) Normalizar
    df["home_team_norm"] = normalize_team_name(df["home_team"])
    df["away_team_norm"] = normalize_team_name(df["away_team"])

    rank["team_norm"] = normalize_team_name(rank["team"])
    if rank["points"].dtype == "object":
        rank["points"] = rank["points"].astype(str).str.replace(",", "", regex=False).astype(float)
    rank = rank[["team_norm", "position", "points"]].copy()

    # 3) Aplicar mapping (si existe)
    mapping = load_mapping(IN_MAPPING)
    if mapping:
        df["home_team_norm"] = df["home_team_norm"].replace(mapping)
        df["away_team_norm"] = df["away_team_norm"].replace(mapping)
        print(f"Mapping aplicado: {len(mapping)} reglas desde {IN_MAPPING}")
    else:
        print("No se encontró mapping; se ejecuta sin reemplazos.")

    # 4) Merge HOME
    df = df.merge(
        rank.rename(columns={
            "team_norm": "home_team_norm",
            "position": "home_rank_position",
            "points": "home_rank_points"
        }),
        on="home_team_norm",
        how="left"
    )

    # 5) Merge AWAY
    df = df.merge(
        rank.rename(columns={
            "team_norm": "away_team_norm",
            "position": "away_rank_position",
            "points": "away_rank_points"
        }),
        on="away_team_norm",
        how="left"
    )

    # 6) Features
    df["rank_points_diff"] = df["home_rank_points"] - df["away_rank_points"]

    df["match_outcome"] = 0
    df.loc[df["home_score"] > df["away_score"], "match_outcome"] = 1
    df.loc[df["home_score"] < df["away_score"], "match_outcome"] = -1

    # 7) Reporte
    home_match = df["home_rank_points"].notna().mean()
    away_match = df["away_rank_points"].notna().mean()
    both_match = (df["home_rank_points"].notna() & df["away_rank_points"].notna()).mean()

    print("\n=== MATCH RATE (Ranking FIFA) ===")
    print(f"Home match: {home_match:.2%}")
    print(f"Away match: {away_match:.2%}")
    print(f"Both match: {both_match:.2%}")

    missing_home = df[df["home_rank_points"].isna()]["home_team_norm"].value_counts().head(30)
    missing_away = df[df["away_rank_points"].isna()]["away_team_norm"].value_counts().head(30)

    print("\nTop 30 HOME teams sin match:")
    print(missing_home)
    print("\nTop 30 AWAY teams sin match:")
    print(missing_away)

    # 8) Guardar
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print("\nCURATED guardado en:", OUT_FILE)


if __name__ == "__main__":
    main()
