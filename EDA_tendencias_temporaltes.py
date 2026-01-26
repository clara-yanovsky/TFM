import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
df = pd.read_csv("outputs/matches_prepared.csv", parse_dates=["date"])

#asegurar fechas válidas
df_time=df.dropna(subset=["date"]).copy()
if df_time.empty:
    print("No hay fechas válidas en 'date'; no se puede hacer serie temporal anual.")
else:
    df_time["year"] = df_time["date"].dt.year

#metricas por año
annual = (
    df_time.groupby("year").agg(
        partidos=("match_key","count") if "match_key" in df_time.columns else ("home_team", "count"),
        goles_promedio=("total_goals","mean"),
        tasa_empate=("result_label", lambda s: (s=="home_win").mean())
    ).reset_index()
)
print(annual.head())
annual.to_csv(os.path.join(OUTPUT_DIR, "temporal_metrics_por_anio.csv"), index=False)

#Gráficos
plt.figure(figsize=(12,6))
sns.lineplot(data=annual, x="year", y="goles_promedio", marker="o")
plt.title("Promedio de goles por año")
plt.xlabel("Año")
plt.ylabel("Goles por partido")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Goles_promedio_por_anio.png"), dpi=200)
plt.close()

plt.figure(figsize=(12,6))
sns.lineplot(data=annual, x="year", y="tasa_empate", markers="o", label="Empate")
sns.lineplot(data=annual, x="year", y="tasa_victoria_local", marker="o", label="Victoria local")
plt.title("Tasas de resultado por año")
plt.xlabel("Año")
plt.ylabel("Proporción")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "tasas_resltado_por_anio.png"), dpi=200)
plt.close()

#Rolling de 365 dias (si el detalle de fechas lo permite)
df_time = df_time.sort_values("date")
roll = (
    df_time.set_index("date")
    .assign(
        goles_promedio=df_time["total_goals"].rolling("365D").mean(),
        tasa_empate=(df_time["result_label"]=="draw").rolling("365D").mean()
    )
    .drop(columns=df_time.columns.difference(["goles_promedio","tasa_empate","tasa_victoria_local"], sort=False))
    .dropna()
    .reset_index()
)
if not roll.empty:
    roll.to_csv(os.path.join(OUTPUT_DIR, "temporal_metrics_rolling_356.csv"), index=False)

plt.figure(figsize=(12,6))
sns.lineplot(data=roll, x="date", y="goles_promedio")
plt.title("Promedio de goles (ventana móvil 365 días)")
plt.xlabel("Fecha")
plt.ylabel("Goles por partido")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "goles_promedio_rolling_365d.png"), dpi=200)
plt.close()
