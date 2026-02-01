from __future__ import annotations

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 80)

# -----------------------------
# PATHS
# -----------------------------
PATH_EMP = "III_2025_Serie-storiche_offerta-di-lavoro_grezzi.xlsx"
PATH_HOURS = "Monte ore lavorate (base 2015) (IT1,534_1037_DF_DCSC_ORE10_2_1,1.0) (2).xlsx"
PATH_GDP = "Prodotto interno lordo e variazioni (stima preliminare) (IT1,163_156_DF_DCCN_SQCQ_3,1.0).xlsx"

START_QUARTER = "2015-Q1"

# -----------------------------
# PIL (parametri noti)
# -----------------------------
GDP_SHEET = "Q IT B1GQ_B_W2_S1 Y 2026M1_1"
GDP_HEADER = 7
GDP_TIME_COL = "Tempo"
GDP_VALUE_ROW_LABEL = "Valori concatenati con anno di riferimento 2020"
GDP_VALUE_ROW_LABEL_FALLBACK = "Valori concatenati"

# -----------------------------
# HELPERS
# -----------------------------
def parse_quarter_to_period(q: str) -> pd.Period:
    m = re.match(r"^(\d{4})-Q([1-4])$", str(q).strip())
    if not m:
        raise ValueError(f"Quarter non valido: {q}")
    return pd.Period(year=int(m.group(1)), quarter=int(m.group(2)), freq="Q")

def safe_numeric(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str) and x.strip() == "..":
        return np.nan
    return pd.to_numeric(x, errors="coerce")

def rebase_to_2015_100(s: pd.Series) -> pd.Series:
    base = s.loc[s.index.year == 2015].mean()
    if pd.isna(base) or base == 0:
        raise ValueError("Base 2015 non calcolabile.")
    return 100 * s / base

def cut_from_start(s: pd.Series, start_q: str) -> pd.Series:
    return s.loc[s.index >= parse_quarter_to_period(start_q)]

def quarter_cols(cols):
    return [c.strip() for c in cols if re.match(r"^\d{4}-Q[1-4]$", c.strip())]

def _norm_label(s: str) -> str:
    s = str(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip().lower()

# -----------------------------
# OCCUPATI
# -----------------------------
def load_employment_total() -> pd.Series:
    df = pd.read_excel(PATH_EMP, sheet_name="Tabella 1", header=3)
    df.columns = [c.strip() for c in df.columns]

    df = df[["Periodo", "Unnamed: 1", "Occupati"]].dropna(subset=["Unnamed: 1"])
    df["Periodo"] = df["Periodo"].ffill()

    df["quarter"] = df.apply(
        lambda r: f"{int(r['Periodo'])}-Q{['I','II','III','IV'].index(r['Unnamed: 1'].split()[0])+1}",
        axis=1
    )
    df["period"] = df["quarter"].apply(parse_quarter_to_period)

    s = pd.to_numeric(df["Occupati"], errors="coerce")
    return pd.Series(s.values, index=df["period"]).sort_index()

# -----------------------------
# ORE LAVORATE (robusto)
# -----------------------------
def load_hours_total(
    sheet_name="Q IT MHOUR_JV_2 Y W_GE1",
    row_label="TOTALE INDUSTRIA E SERVIZI  (b-n)",
    header=7,
) -> pd.Series:
    df = pd.read_excel(PATH_HOURS, sheet_name=sheet_name, header=header)
    df.columns = [c.strip() for c in df.columns]

    label_col = df.columns[0]
    qcols = quarter_cols(df.columns)

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
    s = pd.Series({c: safe_numeric(row[c]) for c in qcols})
    s.index = [parse_quarter_to_period(c) for c in s.index]
    return s.sort_index()

# -----------------------------
# PIL (wide)
# -----------------------------
def load_gdp_wide() -> pd.Series:
    df = pd.read_excel(PATH_GDP, sheet_name=GDP_SHEET, header=GDP_HEADER)
    df.columns = [c.strip() for c in df.columns]

    labels_norm = df[GDP_TIME_COL].astype(str).map(_norm_label)
    hit = df[labels_norm == _norm_label(GDP_VALUE_ROW_LABEL)]

    if hit.shape[0] == 0:
        hit = df[labels_norm.str.contains(_norm_label(GDP_VALUE_ROW_LABEL_FALLBACK), na=False)]

    if hit.shape[0] != 1:
        raise ValueError("Riga PIL non identificata in modo univoco.")

    row = hit.iloc[0]
    qcols = quarter_cols(df.columns)

    s = pd.Series({c: safe_numeric(row[c]) for c in qcols})
    s.index = [parse_quarter_to_period(c) for c in s.index]
    return s.sort_index()

# -----------------------------
# PLOT + SAVE
# -----------------------------
def plot_and_save(gdp_idx, emp_idx, hours_idx):
    footer = "Fonte: ISTAT – Elaborazione Nazareno Lecis"

    # PIL vs Occupati
    df1 = pd.concat([gdp_idx, emp_idx], axis=1).dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    df1.plot(ax=ax)
    ax.set_title("Italia – PIL e Occupati (base 2015=100)")
    ax.set_ylabel("Indice (2015=100)")
    fig.text(0.5, 0.01, footer, ha="center", fontsize=9)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig("pil_vs_occupati_2015_100.png", dpi=300)
    plt.close()

    # PIL vs Ore lavorate
    df2 = pd.concat([gdp_idx, hours_idx], axis=1).dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    df2.plot(ax=ax)
    ax.set_title("Italia – PIL e Ore lavorate (base 2015=100)")
    ax.set_ylabel("Indice (2015=100)")
    fig.text(0.5, 0.01, footer, ha="center", fontsize=9)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig("pil_vs_ore_lavorate_2015_100.png", dpi=300)
    plt.close()

# -----------------------------
# MAIN
# -----------------------------
def main():
    emp = rebase_to_2015_100(cut_from_start(load_employment_total(), START_QUARTER))
    emp.name = "Occupati"

    hours = rebase_to_2015_100(cut_from_start(load_hours_total(), START_QUARTER))
    hours.name = "Ore lavorate"

    gdp = rebase_to_2015_100(cut_from_start(load_gdp_wide(), START_QUARTER))
    gdp.name = "PIL"

    print(pd.concat([gdp, emp, hours], axis=1).tail(8))
    plot_and_save(gdp, emp, hours)

if __name__ == "__main__":
    main()
