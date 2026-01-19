import os
import pandas as pd

IN_API = "data/curated/api_matches_curated.csv"
IN_RANK = "data/processed/football_ranking/ranking_processed.csv"
IN_MAPPING = "data/processed/mappings/team_name_mapping.csv"  # el mismo que usaste para Kaggle

OUT_DIR = "data/curated"
OUT_FILE = os.path.join(OUT_DIR, "api_matches_with_ranking.csv")

os.makedirs(OUT_DIR, exist_ok=True)

def normalize_team_name(s: pd.Series) -> pd.Series:
    # Arreglo encoding + limpieza
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
    try:
        m = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        m = pd.read_csv(path, encoding="cp1252")
    m["kaggle_name"] = normalize_team_name(m["kaggle_name"])
    m["ranking_name"] = normalize_team_name(m["ranking_name"])
    return dict(zip(m["kaggle_name"], m["ranking_name"]))

def main():
    df = pd.read_csv(IN_API, parse_dates=["date"])
    rank = pd.read_csv(IN_RANK)

    df["home_team_norm"] = normalize_team_name(df["home_team"])
    df["away_team_norm"] = normalize_team_name(df["away_team"])

    rank["team_norm"] = normalize_team_name(rank["team"])
    if rank["points"].dtype == "object":
        rank["points"] = rank["points"].astype(str).str.replace(",", "", regex=False).astype(float)
    rank = rank[["team_norm", "position", "points"]].copy()

    # Aplicar mapping que ya usaste (Kaggle -> Ranking)
    mapping = load_mapping(IN_MAPPING)
    if mapping:
        df["home_team_norm"] = df["home_team_norm"].replace(mapping)
        df["away_team_norm"] = df["away_team_norm"].replace(mapping)
        print(f"Mapping aplicado: {len(mapping)} reglas desde {IN_MAPPING}")
    else:
        print("Sin mapping (OK).")

    # Merge HOME
    df = df.merge(
        rank.rename(columns={
            "team_norm": "home_team_norm",
            "position": "home_rank_position",
            "points": "home_rank_points"
        }),
        on="home_team_norm",
        how="left"
    )

    # Merge AWAY
    df = df.merge(
        rank.rename(columns={
            "team_norm": "away_team_norm",
            "position": "away_rank_position",
            "points": "away_rank_points"
        }),
        on="away_team_norm",
        how="left"
    )

    df["rank_points_diff"] = df["home_rank_points"] - df["away_rank_points"]

    # Reporte
    home_match = df["home_rank_points"].notna().mean()
    away_match = df["away_rank_points"].notna().mean()
    both_match = (df["home_rank_points"].notna() & df["away_rank_points"].notna()).mean()

    print("\n=== MATCH RATE (Ranking FIFA) API ===")
    print(f"Home match: {home_match:.2%}")
    print(f"Away match: {away_match:.2%}")
    print(f"Both match: {both_match:.2%}")

    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print("\nCURATED guardado en:", OUT_FILE)

if __name__ == "__main__":
    main()
