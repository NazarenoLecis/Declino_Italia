from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 100)


# =============================================================================
# PATHS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
DATA_DIR = ROOT_DIR / "dati" / "istat"
OUTDIR = BASE_DIR / "output"
OUTDIR.mkdir(exist_ok=True)

PATH_EMP = DATA_DIR / "III_2025_Serie-storiche_offerta-di-lavoro_grezzi.xlsx"
PATH_HOURS = DATA_DIR / "Monte ore lavorate (base 2021) (IT1,534_1037_DF_DCSC_ORE10_2_7,1.0).xlsx"
PATH_GDP = DATA_DIR / "Prodotto interno lordo e variazioni (stima preliminare) (IT1,163_156_DF_DCCN_SQCQ_3,1.0).xlsx"

START_QUARTER = "2015-Q1"
BASE_YEAR = 2015

# PIL: riga valore reale/destagionalizzato nel file ISTAT.
GDP_HEADER = 7
GDP_TIME_COL = "Tempo"
GDP_VALUE_ROW_LABEL = "Valori concatenati con anno di riferimento 2020"
GDP_VALUE_ROW_LABEL_FALLBACK = "Valori concatenati"

# Ore lavorate: base 2021, dati destagionalizzati, imprese con 1+ dipendenti.
HOURS_SHEET = "Q IT MHOUR_JV_2021 Y W_GE1"
HOURS_HEADER = 7
HOURS_TOTAL_ROW = "TOTALE INDUSTRIA E SERVIZI  (b-n)"

FOOTNOTE = "Fonte: ISTAT - Elaborazione Nazareno Lecis"


# =============================================================================
# HELPERS
# =============================================================================
def trimestre_a_periodo(q: str) -> pd.Period:
    m = re.match(r"^(\d{4})-Q([1-4])$", str(q).strip())
    if not m:
        raise ValueError(f"Quarter non valido: {q}")
    return pd.Period(year=int(m.group(1)), quarter=int(m.group(2)), freq="Q")


def numero_sicuro(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str) and x.strip() == "..":
        return np.nan
    return pd.to_numeric(x, errors="coerce")


def indicizza_anno_base_100(s: pd.Series, base_year: int = BASE_YEAR) -> pd.Series:
    base = s.loc[s.index.year == base_year].mean()
    if pd.isna(base) or base == 0:
        raise ValueError(f"Base {base_year} non calcolabile.")
    return 100 * s / base


def taglia_da_trimestre(s: pd.Series, start_q: str) -> pd.Series:
    return s.loc[s.index >= trimestre_a_periodo(start_q)]


def colonne_trimestri(cols) -> list[str]:
    return [str(c).strip() for c in cols if re.match(r"^\d{4}-Q[1-4]$", str(c).strip())]


def _norm_label(s: str) -> str:
    s = str(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def verifica_file_input(paths: list[Path]) -> None:
    missing = [p for p in paths if not p.exists()]
    if missing:
        msg = "\n".join(str(p) for p in missing)
        raise FileNotFoundError(f"File di input mancanti:\n{msg}")


def ultimo_foglio_pil(path: Path) -> str:
    """Sceglie l'ultima edizione ISTAT del PIL nel file Excel."""
    xl = pd.ExcelFile(path)
    candidates = [s for s in xl.sheet_names if s.startswith("Q IT B1GQ")]
    if not candidates:
        raise ValueError(f"Nessun foglio PIL trimestrale trovato in {path.name}.")
    return candidates[-1]


# =============================================================================
# OCCUPATI
# =============================================================================
def carica_occupati_totali(path: Path = PATH_EMP) -> pd.Series:
    df = pd.read_excel(path, sheet_name="Tabella 1", header=3)
    df.columns = [str(c).strip() for c in df.columns]

    df = df[["Periodo", "Unnamed: 1", "Occupati"]].dropna(subset=["Unnamed: 1"]).copy()
    df["Periodo"] = df["Periodo"].ffill()

    roman_to_quarter = {"I": 1, "II": 2, "III": 3, "IV": 4}

    def row_to_period(row) -> pd.Period:
        quarter_token = str(row["Unnamed: 1"]).split()[0]
        return pd.Period(year=int(row["Periodo"]), quarter=roman_to_quarter[quarter_token], freq="Q")

    df["period"] = df.apply(row_to_period, axis=1)
    values = pd.to_numeric(df["Occupati"], errors="coerce")
    return pd.Series(values.values, index=df["period"], name="Occupati").sort_index()


# =============================================================================
# ORE LAVORATE
# =============================================================================
def carica_ore_lavorate_totali(
    path: Path = PATH_HOURS,
    sheet_name: str = HOURS_SHEET,
    row_label: str = HOURS_TOTAL_ROW,
    header: int = HOURS_HEADER,
) -> pd.Series:
    df = pd.read_excel(path, sheet_name=sheet_name, header=header)
    df.columns = [str(c).strip() for c in df.columns]

    label_col = df.columns[0]
    qcols = colonne_trimestri(df.columns)

    labels_norm = df[label_col].astype(str).map(_norm_label)
    target = _norm_label(row_label)

    hit = df[labels_norm == target]
    if hit.shape[0] == 0:
        hit = df[
            labels_norm.str.contains(r"\(b-n\)", na=False)
            & labels_norm.str.contains("industria", na=False)
            & labels_norm.str.contains("servizi", na=False)
        ]

    if hit.shape[0] != 1:
        raise ValueError("Riga ore non identificata in modo univoco.")

    row = hit.iloc[0]
    s = pd.Series({c: numero_sicuro(row[c]) for c in qcols})
    s.index = [trimestre_a_periodo(c) for c in s.index]
    return s.sort_index().rename("Ore lavorate")


# =============================================================================
# PIL
# =============================================================================
def carica_pil_trimestrale(path: Path = PATH_GDP, sheet_name: str | None = None) -> pd.Series:
    sheet = sheet_name or ultimo_foglio_pil(path)
    df = pd.read_excel(path, sheet_name=sheet, header=GDP_HEADER)
    df.columns = [str(c).strip() for c in df.columns]

    labels_norm = df[GDP_TIME_COL].astype(str).map(_norm_label)
    hit = df[labels_norm == _norm_label(GDP_VALUE_ROW_LABEL)]

    if hit.shape[0] == 0:
        hit = df[labels_norm.str.contains(_norm_label(GDP_VALUE_ROW_LABEL_FALLBACK), na=False)]

    if hit.shape[0] != 1:
        raise ValueError(f"Riga PIL non identificata in modo univoco nel foglio '{sheet}'.")

    row = hit.iloc[0]
    qcols = colonne_trimestri(df.columns)

    s = pd.Series({c: numero_sicuro(row[c]) for c in qcols})
    s.index = [trimestre_a_periodo(c) for c in s.index]
    return s.sort_index().rename("PIL")


# =============================================================================
# OUTPUT
# =============================================================================
def costruisci_pannello_pil_lavoro(start_q: str = START_QUARTER, base_year: int = BASE_YEAR) -> pd.DataFrame:
    emp = indicizza_anno_base_100(taglia_da_trimestre(carica_occupati_totali(), start_q), base_year)
    hours = indicizza_anno_base_100(taglia_da_trimestre(carica_ore_lavorate_totali(), start_q), base_year)
    gdp = indicizza_anno_base_100(taglia_da_trimestre(carica_pil_trimestrale(), start_q), base_year)

    panel = pd.concat([gdp, emp, hours], axis=1).dropna(how="all")
    panel.index = panel.index.astype(str)
    panel.index.name = "quarter"
    panel["prod_per_occupied_idx"] = 100 * panel["PIL"] / panel["Occupati"]
    panel["prod_per_hour_idx"] = 100 * panel["PIL"] / panel["Ore lavorate"]
    return panel.reset_index()


def salva_grafici_pil_lavoro(panel: pd.DataFrame, base_year: int = BASE_YEAR) -> None:
    plot_df = panel.set_index("quarter")

    specs = [
        (
            ["PIL", "Occupati"],
            f"Italia - PIL e occupati (base {base_year}=100)",
            OUTDIR / f"pil_vs_occupati_{base_year}_100.png",
        ),
        (
            ["PIL", "Ore lavorate"],
            f"Italia - PIL e ore lavorate (base {base_year}=100)",
            OUTDIR / f"pil_vs_ore_lavorate_{base_year}_100.png",
        ),
        (
            ["prod_per_occupied_idx", "prod_per_hour_idx"],
            f"Italia - produttivita implicita (base {base_year}=100)",
            OUTDIR / f"produttivita_implicita_{base_year}_100.png",
        ),
    ]

    for columns, title, outpath in specs:
        fig, ax = plt.subplots(figsize=(9, 5))
        plot_df[columns].dropna(how="all").plot(ax=ax)
        ax.set_title(title)
        ax.set_ylabel(f"Indice (base {base_year}=100)")
        ax.tick_params(axis="x", rotation=45)
        fig.text(0.5, 0.01, FOOTNOTE, ha="center", fontsize=9)
        plt.tight_layout(rect=[0, 0.04, 1, 1])
        fig.savefig(outpath, dpi=300)
        plt.close(fig)


# Alias compatibili con notebook/script precedenti.
parse_quarter_to_period = trimestre_a_periodo
safe_numeric = numero_sicuro
rebase_to_year_100 = indicizza_anno_base_100
cut_from_start = taglia_da_trimestre
quarter_cols = colonne_trimestri
ensure_inputs_exist = verifica_file_input
latest_gdp_sheet = ultimo_foglio_pil
load_employment_total = carica_occupati_totali
load_hours_total = carica_ore_lavorate_totali
load_gdp_wide = carica_pil_trimestrale
build_panel = costruisci_pannello_pil_lavoro
plot_and_save = salva_grafici_pil_lavoro


def main() -> None:
    verifica_file_input([PATH_EMP, PATH_HOURS, PATH_GDP])
    panel = costruisci_pannello_pil_lavoro()
    out_csv = OUTDIR / f"pil_lavoro_produttivita_base{BASE_YEAR}.csv"
    panel.to_csv(out_csv, index=False, encoding="utf-8")

    print(panel.tail(8).to_string(index=False))
    print(f"[SAVED] {out_csv}")
    salva_grafici_pil_lavoro(panel)
    print(f"[SAVED] Grafici in {OUTDIR}")


if __name__ == "__main__":
    main()
