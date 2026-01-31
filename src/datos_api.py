import os
import json
import time
from datetime import datetime
import requests
import pandas as pd


# =========================
# CONFIGURACION
# =========================
BASE = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": "3eb2c625a66eacbc5980e3e3adf30f63"
}

LEAGUES = [
  {"id": 1, "name": "World Cup"},
  {"id": 10, "name": "Friendlies"},
  {"id": 5, "name": "UEFA Nations League"},
  {"id": 9, "name": "Copa America"},
  {"id": 4, "name": "Euro Championship"},
  {"id": 960, "name": "Euro Championship - Qualification"},
  {"id": 29, "name": "World Cup - Qualification Africa"},
  {"id": 30, "name": "World Cup - Qualification Asia"},
  {"id": 31, "name": "World Cup - Qualification CONCACAF"},
  {"id": 32, "name": "World Cup - Qualification Europe"},
  {"id": 37, "name": "World Cup - Qualification Intercontinental Play-offs"},
  {"id": 33, "name": "World Cup - Qualification Oceania"},
  {"id": 34, "name": "World Cup - Qualification South America"},
]

SEASONS = [2022, 2023, 2024]

OUT_DIR = "data/raw/api_football"
FIXTURES_DIR = os.path.join(OUT_DIR, "fixtures")
MANIFEST_PATH = os.path.join(FIXTURES_DIR, "manifest_fixtures.csv")


# =========================
# HELPERS
# =========================
def safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in s).strip("_")


def api_get(endpoint: str, params: dict) -> dict:
    url = f"{BASE}{endpoint}"
    r = requests.get(url, headers=HEADERS, params=params, timeout=60)
    # Si hay error HTTP, igual intentamos leer cuerpo para logging
    if r.status_code != 200:
        raise Exception(f"HTTP {r.status_code} | {r.text[:300]}")
    return r.json()


def save_json(path: str, payload: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs(FIXTURES_DIR, exist_ok=True)

    manifest_rows = []
    run_ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    for league in LEAGUES:
        league_id = league["id"]
        league_name = league["name"]
        league_folder = os.path.join(FIXTURES_DIR, f"league_{league_id}_{safe_name(league_name)}")
        os.makedirs(league_folder, exist_ok=True)

        for season in SEASONS:
            params = {"league": league_id, "season": season}
            endpoint = "/fixtures"
            extract_ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            out_file = os.path.join(
                league_folder,
                f"fixtures_league_{league_id}_season_{season}_{extract_ts}.json"
            )

            status = "OK"
            error_msg = ""
            results = None
            paging = None
            response_count = 0

            try:
                data = api_get(endpoint, params=params)

                # Validaciones suaves (sin transformar)
                results = data.get("results")
                paging = data.get("paging")
                resp = data.get("response", [])
                response_count = len(resp)

                save_json(out_file, data)

                print(f"[OK] League={league_id} Season={season} -> fixtures={response_count} | saved={out_file}")

            except Exception as e:
                status = "ERROR"
                error_msg = str(e)
                print(f"[ERROR] League={league_id} Season={season} -> {error_msg}")

                # Guardar también el error como “raw” para evidencia si quieres
                err_payload = {
                    "endpoint": endpoint,
                    "params": params,
                    "error": error_msg,
                    "timestamp": extract_ts
                }
                out_file = os.path.join(
                    league_folder,
                    f"ERROR_fixtures_league_{league_id}_season_{season}_{extract_ts}.json"
                )
                save_json(out_file, err_payload)

            manifest_rows.append({
                "run_id": run_ts,
                "extract_timestamp": extract_ts,
                "league_id": league_id,
                "league_name": league_name,
                "season": season,
                "endpoint": endpoint,
                "params": json.dumps(params, ensure_ascii=False),
                "results_field": results,
                "paging_field": json.dumps(paging, ensure_ascii=False) if paging is not None else "",
                "response_count": response_count,
                "status": status,
                "error": error_msg,
                "raw_file_path": out_file
            })

            # Pausa pequeña para no bombardear la API
            time.sleep(0.5)

    df_manifest = pd.DataFrame(manifest_rows)
    df_manifest.to_csv(MANIFEST_PATH, index=False, encoding="utf-8")
    print("\nManifest guardado en:", MANIFEST_PATH)

    # Resumen final útil para tu reporte
    ok = df_manifest[df_manifest["status"] == "OK"]
    print("Extracciones OK:", len(ok), "de", len(df_manifest))
    print("Total fixtures (suma):", ok["response_count"].sum())


if __name__ == "__main__":
    main()
