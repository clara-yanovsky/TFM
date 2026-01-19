import glob
import pandas as pd

files = glob.glob("data/raw/football_ranking/*.csv")
dfs = [pd.read_csv(f) for f in files]

df_rank = pd.concat(dfs, ignore_index=True)

df_rank["points"] = df_rank["points"].astype(str).str.replace(",", "").astype(float)
df_rank["team"] = df_rank["team"].str.replace(r"\s*\(.*\)", "", regex=True)

df_rank = df_rank.drop_duplicates(subset=["team"])

df_rank.to_csv("data/processed/football_ranking/ranking_processed.csv", index=False)
