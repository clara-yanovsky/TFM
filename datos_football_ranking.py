import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://football-ranking.com/fifa-rankings"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


# --- helpers de parsing (NO dependen de índices fijos) ---

RANK_RE = re.compile(r"^\s*(\d+)\b")
TEAM_CODE_RE = re.compile(r"\([A-Z]{3}\)")
DECIMAL_NUMBER_RE = re.compile(r"\b\d{1,3}(?:,\d{3})*\.\d+\b")  # 1,877.18 o 799.80


def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        raise Exception(f"Error HTTP {r.status_code} al descargar {url}")
    return r.text


def find_ranking_table(soup: BeautifulSoup):
    """
    Devuelve la tabla del ranking o None si la página no contiene tablas (fin paginación).
    """
    tables = soup.find_all("table")
    if not tables:
        return None

    keywords = ["rank", "team", "current", "point", "prev"]
    for t in tables:
        headers = [th.get_text(" ", strip=True).lower() for th in t.find_all("th")]
        if headers:
            hits = sum(any(k in h for k in keywords) for h in headers)
            if hits >= 2:
                return t

    return tables[0]


def extract_period_label(soup: BeautifulSoup) -> str:
    """
    Extrae la fecha/periodo visible (ej. '19 January 2026') si está en la página.
    """
    text = soup.get_text("\n", strip=True)
    m = re.search(r"Period\s*\n\s*([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})", text)
    return m.group(1) if m else "unknown_period"


def parse_rank_from_row(row: BeautifulSoup) -> int | None:
    # Tomar el texto completo de la fila y capturar el número inicial
    row_text = row.get_text(" ", strip=True)
    m = RANK_RE.match(row_text)
    if not m:
        return None
    rank = int(m.group(1))
    return rank if 1 <= rank <= 210 else None


def parse_team_from_row(row: BeautifulSoup) -> str | None:
    # Buscar la celda que contiene el código (AAA) típico: "Spain (ESP)"
    tds = row.find_all("td")
    for td in tds:
        cell = td.get_text(" ", strip=True)
        if TEAM_CODE_RE.search(cell):
            return cell
    return None


def parse_current_points_from_row(row: BeautifulSoup) -> str | None:
    # El "Current Point" suele ser el primer número con decimales en la fila
    row_text = row.get_text(" ", strip=True)
    m = DECIMAL_NUMBER_RE.search(row_text)
    return m.group(0) if m else None


def extract_ranking_from_table(table) -> pd.DataFrame:
    data = []

    for row in table.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) == 0:
            continue

        rank = parse_rank_from_row(row)
        if rank is None:
            continue

        team = parse_team_from_row(row)
        if not team:
            continue

        points = parse_current_points_from_row(row)
        if not points:
            continue

        data.append([rank, team, points])

    df = pd.DataFrame(data, columns=["position", "team", "points"])
    return df


def save_raw_per_page(df: pd.DataFrame, out_dir: str, page: int, period: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    safe_period = re.sub(r"\s+", "_", period.strip())
    path = os.path.join(out_dir, f"football_ranking_raw_{today}_{safe_period}_page_{page}.csv")
    df.to_csv(path, index=False, encoding="utf-8")
    return path


def validate_full_dataset(all_pages: list[pd.DataFrame]):
    # Validación (no raw): unir, ordenar y revisar cobertura 1..210
    full = pd.concat(all_pages, ignore_index=True)
    full["position"] = full["position"].astype(int)
    full = full.sort_values("position").reset_index(drop=True)

    # Convertir points a float para revisar rangos
    full["points_num"] = full["points"].astype(str).str.replace(",", "", regex=False).astype(float)

    print("\n=== VALIDACION GLOBAL ===")
    print("Total filas combinadas:", len(full))
    print("Min position:", full["position"].min())
    print("Max position:", full["position"].max())
    print("Unique positions:", full["position"].nunique())
    print("Points min/max:", full["points_num"].min(), "/", full["points_num"].max())
    print(full.head(12))

    missing = sorted(set(range(1, 211)) - set(full["position"].tolist()))
    print("Missing positions count:", len(missing))
    if missing:
        print("Missing positions (primeras 30):", missing[:30])

    dups = full[full.duplicated(subset=["position"], keep=False)].sort_values("position")
    if not dups.empty:
        print("\n⚠️ Duplicados de position (muestra):")
        print(dups.head(20))


def main():
    out_dir = "data/raw"
    all_pages = []
    page = 1

    while True:
        url = f"{BASE_URL}?page={page}"
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        period = extract_period_label(soup)
        table = find_ranking_table(soup)

        if table is None:
            print(f"Page {page} | sin tabla -> fin de paginación")
            break

        df = extract_ranking_from_table(table)
        print(f"Page {page} | period={period} | filas extraídas={len(df)}")

        if len(df) == 0:
            # Si una página no trae filas válidas, parar
            break

        save_raw_per_page(df, out_dir=out_dir, page=page, period=period)
        all_pages.append(df)

        # Si viene corta, normalmente es la última
        if len(df) < 50:
            print("Última página detectada (<50 filas). Fin.")
            break

        page += 1

    if all_pages:
        validate_full_dataset(all_pages)


if __name__ == "__main__":
    main()
