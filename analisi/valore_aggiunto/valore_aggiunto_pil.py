from __future__ import annotations

import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 250)
pd.set_option("display.max_colwidth", 180)

# =============================================================================
# PATHS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
DATA_DIR = ROOT_DIR / "dati" / "istat"
PATH_VA = DATA_DIR / "Produzione e valore aggiunto per branca di attività (IT1,92_1225_DF_DCCN_ANA1_1,1.0).xlsx"
PATH_HOURS = DATA_DIR / "Monte ore lavorate (base 2021) (IT1,534_1037_DF_DCSC_ORE10_2_7,1.0).xlsx"

# =============================================================================
# PARAMETRI
# =============================================================================
START_YEAR = 2015
BASE_YEAR = 2021  # richiesto: base 2021 per arrivare fino al 2025

# Ore lavorate: nel file ISTAT l’informazione "Correzione" è nel metadata (prime righe).
# Questo foglio è quello che usavi già per base 2015 (destagionalizzati); nel base 2021 spesso è identico come naming.
HOURS_SHEET = "Q IT MHOUR_JV_2021 Y W_GE1"
HOURS_HEADER = 7

OUTDIR = BASE_DIR / "output"
OUTDIR.mkdir(exist_ok=True)

PLOTS_DIR = OUTDIR / "plots_all_sectors"
PLOTS_DIR.mkdir(exist_ok=True)

FOOTNOTE = "Fonte: ISTAT - Elaborazione Nazareno Lecis"

MANUAL_SECTOR_MAPPING = {
    "Trasporti e magazzinaggio": "Trasporto e magazzinaggio",
    "Servizi di alloggio e di ristorazione": "Attività dei servizi di alloggio e di ristorazione",
    "Attività amministrative e di servizi di supporto": "Noleggio, agenzie di viaggio, servizi di supporto alle imprese",
    "Attività artistiche, di intrattenimento e divertimento": "Attività artistiche, sportive, di intrattenimento e divertimento",
    "Industria manifatturiera": "Attività manifatturiere",
    "Fornitura di acqua, reti fognarie, attività di trattamento dei rifiuti e risanamento": "Fornitura di acqua reti fognarie, attività di gestione dei rifiuti e risanamento",
}

# =============================================================================
# HELPERS
# =============================================================================
def clean_label(s: str) -> str:
    s = str(s).strip()
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s)
    return s

def clean_key(s: str) -> str:
    """
    Chiave robusta per matching settori: lowercase, rimozione punteggiatura non informativa,
    spazi normalizzati.
    """
    s = clean_label(s).lower()
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9àèéìòù%()/,\- ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9àèéìòù]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def is_year_col(x) -> bool:
    try:
        y = int(str(x).strip())
        return 1800 <= y <= 2100
    except Exception:
        return False

def parse_quarter_col(c: str) -> pd.Period | None:
    s = str(c).strip()
    m = re.match(r"^(\d{4})-Q([1-4])$", s)
    if not m:
        return None
    return pd.Period(year=int(m.group(1)), quarter=int(m.group(2)), freq="Q")

def detect_header_row_for_va(path: str | Path, sheet_name=0, max_rows: int = 80) -> int:
    """
    Auto-detect header: riga che contiene (i) 'Tempo' e (ii) molte colonne anno.
    """
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=max_rows)
    best = None
    for r in range(raw.shape[0]):
        row = raw.iloc[r].tolist()
        row_str = [str(x).strip() for x in row if pd.notna(x)]
        if not row_str:
            continue

        has_tempo = any(str(x).strip().lower() == "tempo" for x in row_str)
        year_hits = sum(is_year_col(x) for x in row_str)

        if has_tempo and year_hits >= 5:
            score = year_hits
            if best is None or score > best[0]:
                best = (score, r)

    if best is None:
        raise ValueError(
            "Impossibile individuare automaticamente l'header nel file VA.\n"
            "Apri il file e trova la riga con 'Tempo' e le colonne anno (2015, 2016, ...), "
            "poi imposta manualmente la riga in detect_header_row_for_va()."
        )
    return best[1]

def rebase_to_base_year_100(s: pd.Series, base_year: int) -> pd.Series:
    """
    Rebasing su media del base_year.
    """
    s = s.astype(float).copy()
    base = s.loc[s.index == base_year].mean()

    if pd.isna(base) or base == 0:
        raise ValueError(f"Base {base_year} non calcolabile (mancano dati o base=0).")
    return 100.0 * s / base

def add_footnote(fig):
    fig.text(0.01, 0.01, FOOTNOTE, ha="left", va="bottom", fontsize=9)

def save_unmatched(va_sectors, hours_sectors, mapping, outdir: str | Path):
    outdir = Path(outdir)
    va_set = set(va_sectors)
    h_set = set(hours_sectors)
    mapped_va = set(mapping.keys())
    mapped_h = set(mapping.values())

    unmatched_va = sorted(list(va_set - mapped_va))
    unmatched_h = sorted(list(h_set - mapped_h))

    pd.Series(unmatched_va, name="unmatched_va").to_csv(outdir / "unmatched_va_sectors.csv", index=False, encoding="utf-8")
    pd.Series(unmatched_h, name="unmatched_hours").to_csv(outdir / "unmatched_hours_sectors.csv", index=False, encoding="utf-8")

# =============================================================================
# 0) (opzionale) stampa metadata ore (prime righe) per trasparenza
# =============================================================================
def print_hours_metadata(path: str | Path, sheet_name: str, nrows: int = 12):
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=nrows)
    print("\n=== HOURS SHEET METADATA (prime righe) ===")
    print(raw.iloc[:, :12].to_string(index=True))

# =============================================================================
# 1) LOAD: Valore aggiunto annuale (wide -> long)
# =============================================================================
def load_va_annual(path: str | Path, sheet_name=0) -> pd.DataFrame:
    header_row = detect_header_row_for_va(path, sheet_name=sheet_name)

    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
    df.columns = [clean_label(c) for c in df.columns]

    # colonne anno
    year_cols = [c for c in df.columns if is_year_col(c)]
    if not year_cols:
        raise ValueError("Non trovo colonne anno nel file VA (2015, 2016, ...).")

    # colonna settore: se esiste "Tempo", nel tuo file spesso contiene direttamente i settori.
    tempo_candidates = [c for c in df.columns if str(c).strip().lower() == "tempo"]
    sector_col = tempo_candidates[0] if tempo_candidates else df.columns[0]

    out = df[[sector_col] + year_cols].copy()
    out = out.dropna(subset=[sector_col])
    out[sector_col] = out[sector_col].astype(str).map(clean_label)

    long = out.melt(id_vars=[sector_col], var_name="year", value_name="va")
    long["year"] = long["year"].astype(int)
    long["va"] = pd.to_numeric(long["va"].replace("..", np.nan), errors="coerce")

    long = long[long["year"] >= START_YEAR].copy()
    long = long.rename(columns={sector_col: "sector_va"})
    long["key"] = long["sector_va"].map(clean_key)
    return long

# =============================================================================
# 2) LOAD: Ore lavorate trimestrali (wide -> long)
# =============================================================================
def load_hours_quarterly(path: str | Path, sheet_name: str, header: int) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, header=header)
    cols_raw = [str(c).strip() for c in df.columns]
    df.columns = cols_raw

    label_col = cols_raw[0]
    qcols = [c for c in cols_raw[1:] if parse_quarter_col(c) is not None]
    if not qcols:
        raise ValueError(
            f"Nessuna colonna trimestrale 'YYYY-Qk' trovata nel foglio ore '{sheet_name}'. "
            f"Prime colonne: {cols_raw[:25]}"
        )

    tmp = df[[label_col] + qcols].copy()
    tmp = tmp.dropna(subset=[label_col])
    tmp[label_col] = tmp[label_col].astype(str).map(clean_label)

    long = tmp.melt(id_vars=[label_col], var_name="quarter", value_name="hours_idx_q")
    long["period"] = long["quarter"].apply(lambda x: parse_quarter_col(str(x).strip()))
    long = long.dropna(subset=["period"]).copy()
    long["year"] = long["period"].apply(lambda p: p.year)
    long["hours_idx_q"] = pd.to_numeric(long["hours_idx_q"].replace("..", np.nan), errors="coerce")

    long = long[long["year"] >= START_YEAR].copy()
    long = long.rename(columns={label_col: "sector_hours"})
    long["key"] = long["sector_hours"].map(clean_key)
    return long

# =============================================================================
# 3) Annualizza ore (indice trimestrale -> media annua)
# =============================================================================
def annualize_hours_index(hours_q: pd.DataFrame) -> pd.DataFrame:
    g = hours_q.groupby(["key", "sector_hours", "year"], as_index=False)["hours_idx_q"].mean()
    g = g.rename(columns={"hours_idx_q": "hours_idx_annual_raw"})
    return g

# =============================================================================
# 4) Matching settori: exact key + (opzionale) fuzzy se installato
# =============================================================================
def build_sector_mapping(
    va_long: pd.DataFrame,
    hours_a: pd.DataFrame,
    fuzzy_threshold: int = 96,
    use_fuzzy: bool = False,
) -> dict:
    va_sectors = va_long[["key", "sector_va"]].drop_duplicates()
    h_sectors = hours_a[["key", "sector_hours"]].drop_duplicates()

    va_map = dict(zip(va_sectors["key"], va_sectors["sector_va"]))
    h_map = dict(zip(h_sectors["key"], h_sectors["sector_hours"]))

    common_keys = sorted(set(va_map.keys()) & set(h_map.keys()))
    mapping = {va_map[k]: h_map[k] for k in common_keys}  # VA label -> HOURS label

    available_va = set(va_map.values())
    available_hours = set(h_map.values())
    for sector_va, sector_hours in MANUAL_SECTOR_MAPPING.items():
        if sector_va in available_va and sector_hours in available_hours:
            mapping[sector_va] = sector_hours

    # Il fuzzy matching resta disponibile, ma è disattivato di default:
    # nelle branche ATECO label simili possono indicare aggregati diversi.
    if use_fuzzy:
        try:
            from rapidfuzz import process, fuzz  # type: ignore

            unmatched_va = [va_map[k] for k in set(va_map.keys()) - set(common_keys)]
            h_choices = list(h_map.values())

            for s in unmatched_va:
                best = process.extractOne(s, h_choices, scorer=fuzz.token_sort_ratio)
                if best is None:
                    continue
                cand, score, _ = best
                if score >= fuzzy_threshold:
                    mapping[s] = cand
        except Exception:
            pass

    return mapping

# =============================================================================
# 5) Panel: VA_idx e HOURS_idx base BASE_YEAR=100 (per ogni settore)
# =============================================================================
def build_panel(va_long: pd.DataFrame, hours_a: pd.DataFrame, mapping_va_to_hours: dict) -> pd.DataFrame:
    # applica mapping: porta VA -> label ore
    va2 = va_long.copy()
    va2["sector_hours"] = va2["sector_va"].map(mapping_va_to_hours)
    va2 = va2.dropna(subset=["sector_hours"]).copy()

    # unisci con ore annualizzate usando label ore + year
    merged = va2.merge(
        hours_a,
        on=["sector_hours", "year"],
        how="inner",
        suffixes=("_va", "_h"),
    )

    out = []
    for sec_va, sub in merged.groupby("sector_va", sort=False):
        sub2 = sub.sort_values("year").copy()

        va_s = pd.Series(sub2["va"].values, index=sub2["year"].values)
        h_s = pd.Series(sub2["hours_idx_annual_raw"].values, index=sub2["year"].values)

        va_idx = rebase_to_base_year_100(va_s, BASE_YEAR)
        h_idx = rebase_to_base_year_100(h_s, BASE_YEAR)

        sub2["va_idx"] = sub2["year"].map(va_idx)
        sub2["hours_idx"] = sub2["year"].map(h_idx)

        # produttività implicita: VA_idx / HOURS_idx * 100
        sub2["prod_idx"] = (sub2["va_idx"] / sub2["hours_idx"]) * 100.0

        sub2["flag_va_gt_hours"] = (sub2["va_idx"] > sub2["hours_idx"]).astype(int)
        sub2["flag_prod_gt_100"] = (sub2["prod_idx"] > 100.0).astype(int)

        out.append(sub2)

    panel = pd.concat(out, ignore_index=True) if out else merged.assign(va_idx=np.nan, hours_idx=np.nan, prod_idx=np.nan)
    panel = panel[panel["year"] >= START_YEAR].copy()
    return panel

# =============================================================================
# 6) Plot: per OGNI attività -> VA_idx vs HOURS_idx e produttività implicita
# =============================================================================
def plot_sector_va_vs_hours(panel: pd.DataFrame, sector_va: str, outdir: str | Path):
    sub = panel[panel["sector_va"] == sector_va].sort_values("year").copy()
    if sub.empty:
        return

    fig = plt.figure(figsize=(10, 5))
    ax = plt.gca()
    ax.plot(sub["year"], sub["va_idx"], label="Valore aggiunto (indice)")
    ax.plot(sub["year"], sub["hours_idx"], label="Ore lavorate (indice)")
    ax.set_title(f"{sector_va} – VA e Ore (base {BASE_YEAR}=100)")
    ax.set_xlabel("Anno")
    ax.set_ylabel(f"Indice (base {BASE_YEAR}=100)")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    plt.tight_layout()
    add_footnote(fig)

    outpath = Path(outdir) / f"va_vs_hours_{slugify(sector_va)}.png"
    fig.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close(fig)

def plot_sector_productivity(panel: pd.DataFrame, sector_va: str, outdir: str | Path):
    sub = panel[panel["sector_va"] == sector_va].sort_values("year").copy()
    if sub.empty:
        return

    fig = plt.figure(figsize=(10, 5))
    ax = plt.gca()
    ax.plot(sub["year"], sub["prod_idx"])
    ax.axhline(100.0, linestyle="--", linewidth=1)
    ax.set_title(f"{sector_va} – Produttività implicita (VA/Ore), base {BASE_YEAR}=100")
    ax.set_xlabel("Anno")
    ax.set_ylabel(f"Indice (base {BASE_YEAR}=100)")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    add_footnote(fig)

    outpath = Path(outdir) / f"prod_idx_{slugify(sector_va)}.png"
    fig.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close(fig)

# =============================================================================
# MAIN
# =============================================================================
def main():
    # check file existence (errore chiaro se path sbagliato)
    for p in [PATH_VA, PATH_HOURS]:
        if not p.exists():
            raise FileNotFoundError(f"File non trovato: {p} (mettilo nella cartella dello script o correggi PATH)")

    # (opzionale) metadata ore per confermare correzione (destagionalizzato / calendar adjusted, ecc.)
    # Decommenta la riga sotto se vuoi stampare le prime righe del foglio ore.
    # print_hours_metadata(PATH_HOURS, HOURS_SHEET, nrows=12)

    # 1) Carica dati
    va_long = load_va_annual(PATH_VA, sheet_name=0)                    # annuale
    hours_q = load_hours_quarterly(PATH_HOURS, HOURS_SHEET, HOURS_HEADER)  # trimestrale
    hours_a = annualize_hours_index(hours_q)                           # annualizzato

    # 2) Salva i due dataset “puliti” separati (come richiesto)
    va_out = OUTDIR / "va_annual_long.csv"
    hq_out = OUTDIR / "hours_quarterly_long.csv"
    ha_out = OUTDIR / "hours_annualized.csv"
    va_long.to_csv(va_out, index=False, encoding="utf-8")
    hours_q.to_csv(hq_out, index=False, encoding="utf-8")
    hours_a.to_csv(ha_out, index=False, encoding="utf-8")
    print("[SAVED]", va_out)
    print("[SAVED]", hq_out)
    print("[SAVED]", ha_out)

    # 3) Matching settori
    mapping = build_sector_mapping(va_long, hours_a, fuzzy_threshold=96, use_fuzzy=False)

    # diagnostica e file per unmatched
    va_sectors = sorted(va_long["sector_va"].dropna().unique().tolist())
    h_sectors = sorted(hours_a["sector_hours"].dropna().unique().tolist())
    save_unmatched(va_sectors, h_sectors, mapping, OUTDIR)

    mapping_out = OUTDIR / "mapping_va_to_hours.csv"
    pd.DataFrame({"sector_va": list(mapping.keys()), "sector_hours": list(mapping.values())}).to_csv(
        mapping_out, index=False, encoding="utf-8"
    )
    print("[SAVED]", mapping_out)
    print(f"[INFO] Settori matchati: {len(mapping)} (unmatched salvati in output)")

    if len(mapping) == 0:
        raise SystemExit(
            "\nNessun settore matchato.\n"
            "Guarda i file 'unmatched_va_sectors.csv' e 'unmatched_hours_sectors.csv' e poi crea una mappatura manuale.\n"
            "Se vuoi, incollami 20 righe per lato e te la costruisco io."
        )

    # 4) Panel allineato (solo intersezione settore-anno disponibile in entrambi)
    panel = build_panel(va_long, hours_a, mapping)
    panel_out = OUTDIR / f"panel_va_hours_indices_base{BASE_YEAR}.csv"
    panel.to_csv(panel_out, index=False, encoding="utf-8")
    print("[SAVED]", panel_out)

    # 5) Summary: in quanti anni VA_idx > HOURS_idx
    summary = (
        panel.dropna(subset=["va_idx", "hours_idx"])
        .groupby("sector_va", as_index=False)
        .agg(
            years_available=("year", "nunique"),
            years_va_gt_hours=("flag_va_gt_hours", "sum"),
            share_va_gt_hours=("flag_va_gt_hours", "mean"),
            last_year=("year", "max"),
        )
        .sort_values(["years_va_gt_hours", "share_va_gt_hours"], ascending=[False, False])
        .reset_index(drop=True)
    )

    last_rows = (
        panel.sort_values(["sector_va", "year"])
        .groupby("sector_va", as_index=False)
        .tail(1)[["sector_va", "year", "va_idx", "hours_idx", "prod_idx"]]
        .rename(
            columns={
                "year": "last_year_check",
                "va_idx": "va_idx_last",
                "hours_idx": "hours_idx_last",
                "prod_idx": "prod_idx_last",
            }
        )
    )
    summary = summary.merge(last_rows, on="sector_va", how="left")
    summary["gap_va_minus_hours_last"] = summary["va_idx_last"] - summary["hours_idx_last"]

    summary_out = OUTDIR / f"summary_sectors_va_gt_hours_base{BASE_YEAR}.csv"
    summary.to_csv(summary_out, index=False, encoding="utf-8")
    print("[SAVED]", summary_out)

    print("\n=== SUMMARY (top 30) ===")
    print(summary.head(30).to_string(index=False))

    # 6) Grafici per OGNI attività (tutte le attività presenti nel panel)
    sectors = sorted(panel["sector_va"].dropna().unique().tolist())
    for sec in sectors:
        plot_sector_va_vs_hours(panel, sec, PLOTS_DIR)
        plot_sector_productivity(panel, sec, PLOTS_DIR)

    print("[SAVED] Grafici (tutti i settori) in:", PLOTS_DIR)

    # 7) Nota dati
    print("\n=== NOTE DATI ===")
    print("- Valore aggiunto: annuale; dal file 'Produzione e valore aggiunto…' (valori concatenati / reali se così indicato nel file).")
    print(f"- Ore lavorate: trimestrale; foglio '{HOURS_SHEET}' (dati destagionalizzati nel metadata del file).")
    print("- Annualizzazione ore: media dei 4 trimestri (coerente perché la variabile è un indice).")
    print(f"- Indici per settore: base {BASE_YEAR}=100; periodo da {START_YEAR}.")
    print(f"- Footer grafici: {FOOTNOTE}")

if __name__ == "__main__":
    main()
