import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
df = pd.read_csv("outputs/matches_prepared.csv", parse_dates=["date"])

#filtrar filas con ranking disponibles
rank_df = df.dropna(subset=["rank_points_diff", "result_label"]).copy()
#Bins de diferencia de ranking (ajusta el ancho segun tu dispersión)
bin_width=100
min_diff = int(np.floor(rank_df["ranke_points_diff"].min() / bin_width) * bin_width)
max_diff = int(np.ceil(rank_df["rank_points_diff"].max() / bin_width) * bin_width)
bins = np.arange(min_diff, max_diff + bin_width, bin_width)

rank_df["rank_bin"] = pd.cut(rank_df["rank_points_diff"], bins=bins, include_lowest=True)

#Tasa de victoria del local por bin
winrate_by_bin=(
    rank_df.groupby("rank_bin")["result_label"]
    .apply(lambda s:(s=="home_win").mean())
    .reset_index()
    .rename(columns={"result_label":"home_win_rate"})
)

#Conteo por bin (para ver soporte)
count_by_bin=rank_df["rank_bin"].value_counts().sort_index().rename("n").reset_index().rename(columns={"index":"rank_bin"})

summary_bin = pd.merge(winrate_by_bin, count_by_bin, on="rank_bin", how="left")
print(summary_bin.head(10))
summary_bin.to_csv(os.path.join(OUTPUT_DIR, "rankgap_winrate_bins.csv"), index=False)

#Visualización
plt.figure(figsize=(10,5))
sns.llineplot(data=summary_bin, x="rank_bin", y="home_win_rate", marker="o")
plt.xticks(rotation=45)
plt.title("Tasa de victoria del local vs diferencia de ranking (puntos)")
plt.ylabel("Tasa de victoria del local")
plt.xlabel("Bin de diferencia de ranking (home-away)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "rankgap_vs_homewin.png"), dpi=200)
plt.close()

#Estadisticos adicionales
stats = {
    "Correlacion_spearman_rankdiff_homewin": rank_df.assign(home_win=(rank_df["result_label"]=="home_win").astype(int))
    [["rank_points_diff", "home_win"]].corr(method="spearman").iloc[0,1]
}
print(stats)
pd.DataFrame([stats]).to_csv(os.path.join(OUTPUT_DIR, "rankgap_stats.csv"), index=False)

#Calibración simple con regresión logistica
try:
    from sklearn.linear_model import LogisticRegression
    X = rank_df[["rank_points_diff"]].fillna(0).values
    y = (rank_df["result_label"] == "home_win").astype(int).values
    lr = LogisticRegression()
    lr.fit(X,y)
    print("Coeficiente (rank_points_diff):", lr.coef_[0][0], "intercepto:", lr.intercept_[0])
except Exception as e:
    print("Regresión logística no ejecutada:", e)
    