from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

import matplotlib.pyplot as plt
import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = BASE_DIR

WORLD_BANK_COUNTRIES = [
    "ITA",
    "DEU",
    "FRA",
    "ESP",
    "EUU",
    "USA",
    "JPN",
    "GBR",
    "CAN",
    "AUS",
    "AUT",
    "BEL",
    "CHE",
    "DNK",
    "FIN",
    "NLD",
    "NOR",
    "SWE",
    "PRT",
    "GRC",
    "IRL",
]
EUROSTAT_GEOS = ["IT", "DE", "FR", "ES", "EU27_2020"]

COUNTRY_KEY = {
    "ITA": "ITA",
    "DEU": "DEU",
    "FRA": "FRA",
    "ESP": "ESP",
    "EUU": "EU",
    "IT": "ITA",
    "DE": "DEU",
    "FR": "FRA",
    "ES": "ESP",
    "EU27_2020": "EU",
}

COUNTRY_LABEL = {
    "ITA": "Italia",
    "DEU": "Germania",
    "FRA": "Francia",
    "ESP": "Spagna",
    "EU": "Unione europea",
}

PEER_KEYS = ["DEU", "FRA", "ESP", "EU"]

IMPORTANT_PLOT_INDICATORS: tuple[str, ...] = (
    "NY.GDP.PCAP.KD",
    "ESTAT_RLPR_HW_I15",
    "SP.DYN.TFRT.IN",
    "SP.POP.65UP.TO.ZS",
    "GB.XPD.RSDV.GD.ZS",
    "DERIVED_PATENTS_PER_MILLION",
    "PAY.TAX.TM",
    "GOV_WGI_GE.EST",
    "GC.XPN.INTP.RV.ZS",
    "NE.GDI.FTOT.ZS",
    "BN.CAB.XOKA.GD.ZS",
    "NE.CON.PRVT.PC.KD",
)


@dataclass(frozen=True)
class Indicator:
    indicator_id: str
    label: str
    theme: str
    unit: str
    source: str
    bad_when: str
    note: str = ""


WORLD_BANK_INDICATORS: tuple[Indicator, ...] = (
    Indicator("NY.GDP.PCAP.KD", "PIL reale pro capite", "produttivita_reddito", "US$ costanti 2015", "World Bank WDI", "low"),
    Indicator("SL.GDP.PCAP.EM.KD", "PIL per occupato", "produttivita_reddito", "PPP $ costanti", "World Bank WDI", "low"),
    Indicator("NY.GDP.MKTP.KD.ZG", "Crescita reale del PIL", "produttivita_reddito", "% annuo", "World Bank WDI", "low"),
    Indicator("NE.GDI.TOTL.ZS", "Investimenti lordi", "produttivita_reddito", "% PIL", "World Bank WDI", "low"),
    Indicator("SL.EMP.TOTL.SP.ZS", "Tasso di occupazione 15+", "occupazione", "% popolazione 15+", "World Bank WDI", "low"),
    Indicator("SL.UEM.TOTL.ZS", "Tasso di disoccupazione", "occupazione", "% forza lavoro", "World Bank WDI", "high"),
    Indicator("SL.TLF.TOTL.IN", "Forza lavoro totale", "occupazione", "persone", "World Bank WDI", "context"),
    Indicator("SP.POP.TOTL", "Popolazione totale", "demografia", "persone", "World Bank WDI", "context"),
    Indicator("SP.POP.GROW", "Crescita della popolazione", "demografia", "% annuo", "World Bank WDI", "low"),
    Indicator("SP.POP.1564.TO.ZS", "Popolazione in eta 15-64", "demografia", "% totale", "World Bank WDI", "low"),
    Indicator("SP.POP.65UP.TO.ZS", "Popolazione 65+", "demografia", "% totale", "World Bank WDI", "high"),
    Indicator("SP.DYN.TFRT.IN", "Tasso di fertilita", "natalita", "figli per donna", "World Bank WDI", "low"),
    Indicator("SP.DYN.CBRT.IN", "Natalita grezza", "natalita", "nati per 1.000 abitanti", "World Bank WDI", "low"),
    Indicator("GB.XPD.RSDV.GD.ZS", "Spesa in R&S", "innovazione", "% PIL", "World Bank WDI", "low"),
    Indicator("IP.PAT.RESD", "Domande di brevetto residenti", "innovazione", "numero", "World Bank WDI", "context"),
    Indicator("TX.VAL.TECH.MF.ZS", "Export high-tech", "innovazione", "% export manifatturiero", "World Bank WDI", "low"),
    Indicator("SE.TER.ENRR", "Iscrizione terziaria lorda", "capitale_umano", "%", "World Bank WDI", "low"),
    Indicator("PAY.TAX.TOT.TAX.RT.ZS", "Carico fiscale totale sulle imprese", "burocrazia", "% profitti", "World Bank Doing Business", "high"),
    Indicator("PAY.TAX.TM", "Tempo per adempimenti fiscali", "burocrazia", "ore/anno", "World Bank Doing Business", "high"),
    Indicator("IC.REG.DURS.MA.DY", "Tempo per avviare una impresa", "burocrazia", "giorni", "World Bank Doing Business", "high"),
    Indicator("IC.REG.PROC.MA.NO", "Procedure per avviare una impresa", "burocrazia", "numero", "World Bank Doing Business", "high"),
    Indicator("GOV_WGI_GE.EST", "Efficacia del governo", "istituzioni", "stima -2.5/+2.5", "World Bank WGI", "low"),
    Indicator("GOV_WGI_RQ.EST", "Qualita regolatoria", "istituzioni", "stima -2.5/+2.5", "World Bank WGI", "low"),
    Indicator("GOV_WGI_CC.EST", "Controllo della corruzione", "istituzioni", "stima -2.5/+2.5", "World Bank WGI", "low"),
    Indicator("GOV_WGI_RL.EST", "Stato di diritto", "istituzioni", "stima -2.5/+2.5", "World Bank WGI", "low"),
    Indicator("GC.DOD.TOTL.GD.ZS", "Debito pubblico lordo", "finanza_pubblica", "% PIL", "World Bank WDI", "high"),
    Indicator("GC.XPN.TOTL.GD.ZS", "Spesa pubblica totale", "finanza_pubblica", "% PIL", "World Bank WDI", "context"),
    Indicator("GC.REV.XGRT.GD.ZS", "Entrate pubbliche esclusi trasferimenti", "finanza_pubblica", "% PIL", "World Bank WDI", "context"),
    Indicator("GC.TAX.TOTL.GD.ZS", "Entrate fiscali", "finanza_pubblica", "% PIL", "World Bank WDI", "context"),
    Indicator("GC.XPN.INTP.RV.ZS", "Interessi sul debito", "finanza_pubblica", "% entrate", "World Bank WDI", "high"),
    Indicator("NE.GDI.FTOT.ZS", "Formazione lorda di capitale fisso", "investimenti", "% PIL", "World Bank WDI", "low"),
    Indicator("NE.GDI.FTOT.KD.ZG", "Crescita investimenti fissi reali", "investimenti", "% annuo", "World Bank WDI", "low"),
    Indicator("NE.GDI.TOTL.KD.ZG", "Crescita formazione lorda di capitale reale", "investimenti", "% annuo", "World Bank WDI", "low"),
    Indicator("NV.IND.TOTL.KD.ZG", "Crescita valore aggiunto industria", "produzione", "% annuo", "World Bank WDI", "low"),
    Indicator("NV.IND.MANF.KD.ZG", "Crescita valore aggiunto manifattura", "produzione", "% annuo", "World Bank WDI", "low"),
    Indicator("NV.IND.MANF.ZS", "Quota manifattura sul valore aggiunto", "produzione", "% PIL", "World Bank WDI", "low"),
    Indicator("NE.EXP.GNFS.ZS", "Export di beni e servizi", "settore_estero", "% PIL", "World Bank WDI", "context"),
    Indicator("NE.IMP.GNFS.ZS", "Import di beni e servizi", "settore_estero", "% PIL", "World Bank WDI", "context"),
    Indicator("NE.TRD.GNFS.ZS", "Apertura commerciale", "settore_estero", "% PIL", "World Bank WDI", "context"),
    Indicator("BN.CAB.XOKA.GD.ZS", "Saldo delle partite correnti", "settore_estero", "% PIL", "World Bank WDI", "context"),
    Indicator("TT.PRI.MRCH.XD.WD", "Ragioni di scambio merci", "settore_estero", "indice 2015=100", "World Bank WDI", "low"),
    Indicator("FP.CPI.TOTL.ZG", "Inflazione prezzi al consumo", "prezzi_consumi", "% annuo", "World Bank WDI", "context"),
    Indicator("NE.CON.PRVT.KD.ZG", "Crescita consumi privati reali", "prezzi_consumi", "% annuo", "World Bank WDI", "low"),
    Indicator("NE.CON.PRVT.PC.KD", "Consumi privati reali pro capite", "prezzi_consumi", "US$ costanti 2015", "World Bank WDI", "low"),
    Indicator("NY.GNS.ICTR.ZS", "Risparmio nazionale lordo", "risparmio_turismo", "% PIL", "World Bank WDI", "low"),
    Indicator("NY.ADJ.SVNG.GN.ZS", "Risparmio netto aggiustato", "risparmio_turismo", "% RNL", "World Bank WDI", "low"),
    Indicator("ST.INT.ARVL", "Arrivi turistici internazionali", "risparmio_turismo", "numero", "World Bank WDI", "context"),
    Indicator("FR.INR.RINR", "Tasso di interesse reale", "tassi_cambio", "%", "World Bank WDI", "context"),
    Indicator("FR.INR.LEND", "Tasso sui prestiti", "tassi_cambio", "%", "World Bank WDI", "context"),
    Indicator("PX.REX.REER", "Cambio effettivo reale", "tassi_cambio", "indice 2010=100", "World Bank WDI", "context"),
)

EUROSTAT_PRODUCTIVITY_SERIES: tuple[dict[str, str], ...] = (
    {
        "indicator_id": "ESTAT_RLPR_HW_I15",
        "na_item": "RLPR_HW",
        "unit_code": "I15",
        "label": "Produttivita reale per ora lavorata",
        "theme": "produttivita_reddito",
        "unit": "indice 2015=100",
        "bad_when": "low",
        "note": "Eurostat nama_10_lp_ulc, real labour productivity per hour worked.",
    },
    {
        "indicator_id": "ESTAT_RLPR_PER_I15",
        "na_item": "RLPR_PER",
        "unit_code": "I15",
        "label": "Produttivita reale per occupato",
        "theme": "produttivita_reddito",
        "unit": "indice 2015=100",
        "bad_when": "low",
        "note": "Eurostat nama_10_lp_ulc, real labour productivity per person employed.",
    },
    {
        "indicator_id": "ESTAT_NULC_HW_I15",
        "na_item": "NULC_HW",
        "unit_code": "I15",
        "label": "Costo del lavoro per unita di prodotto",
        "theme": "produttivita_reddito",
        "unit": "indice 2015=100",
        "bad_when": "high",
        "note": "Eurostat nama_10_lp_ulc, nominal unit labour cost per hour worked.",
    },
    {
        "indicator_id": "ESTAT_HW_EMP",
        "na_item": "HW_EMP",
        "unit_code": "HW",
        "label": "Ore lavorate per occupato",
        "theme": "produttivita_reddito",
        "unit": "ore annue",
        "bad_when": "context",
        "note": "Eurostat nama_10_lp_ulc, ore annue per persona occupata.",
    },
)


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def world_bank_url(indicator_id: str, countries: Iterable[str] = WORLD_BANK_COUNTRIES) -> str:
    country_path = ";".join(countries)
    return f"https://api.worldbank.org/v2/country/{country_path}/indicator/{indicator_id}"


def eurostat_url(spec: dict[str, str], geos: Iterable[str] = EUROSTAT_GEOS) -> str:
    params = [
        ("freq", "A"),
        ("unit", spec["unit_code"]),
        ("na_item", spec["na_item"]),
        *[("geo", geo) for geo in geos],
    ]
    return "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_lp_ulc?" + urlencode(params)


def fetch_world_bank_indicator(indicator: Indicator, start_year: int = 1995) -> pd.DataFrame:
    params = {"format": "json", "per_page": 20000}
    url = world_bank_url(indicator.indicator_id)
    response = requests.get(url, params=params, timeout=45)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Risposta World Bank inattesa per {indicator.indicator_id}: {payload}")

    rows = []
    for item in payload[1] or []:
        value = item.get("value")
        if value is None:
            continue
        year = int(item["date"])
        if year < start_year:
            continue
        raw_country = item.get("countryiso3code") or item.get("country", {}).get("id")
        key = COUNTRY_KEY.get(raw_country, raw_country)
        rows.append(
            {
                "source": indicator.source,
                "source_url": response.url,
                "indicator_id": indicator.indicator_id,
                "indicator_label": indicator.label,
                "theme": indicator.theme,
                "unit": indicator.unit,
                "bad_when": indicator.bad_when,
                "note": indicator.note,
                "country_raw": raw_country,
                "country_key": key,
                "country": COUNTRY_LABEL.get(key, item.get("country", {}).get("value", raw_country)),
                "year": year,
                "value": float(value),
            }
        )
    return pd.DataFrame(rows)


def fetch_world_bank_panel(start_year: int = 1995) -> pd.DataFrame:
    frames = [fetch_world_bank_indicator(ind, start_year=start_year) for ind in WORLD_BANK_INDICATORS]
    return pd.concat(frames, ignore_index=True)


def year_columns(columns: Iterable[object]) -> list[str]:
    out = []
    for col in columns:
        text = str(col)
        if re.match(r"^\d{4}$", text):
            out.append(text)
    return out


def fetch_eurostat_productivity_panel(start_year: int = 1995) -> pd.DataFrame:
    try:
        import eurostat
    except ImportError as exc:
        raise RuntimeError("Installa il pacchetto 'eurostat' per aggiornare le serie Eurostat.") from exc

    frames: list[pd.DataFrame] = []
    for spec in EUROSTAT_PRODUCTIVITY_SERIES:
        raw = eurostat.get_data_df(
            "nama_10_lp_ulc",
            filter_pars={
                "freq": "A",
                "unit": spec["unit_code"],
                "na_item": spec["na_item"],
                "geo": EUROSTAT_GEOS,
            },
        )
        geo_col = next(c for c in raw.columns if str(c).startswith("geo"))
        ycols = year_columns(raw.columns)
        long = raw.melt(id_vars=[geo_col], value_vars=ycols, var_name="year", value_name="value")
        long = long.rename(columns={geo_col: "country_raw"})
        long["year"] = long["year"].astype(int)
        long["value"] = pd.to_numeric(long["value"], errors="coerce")
        long = long.dropna(subset=["value"])
        long = long[long["year"] >= start_year].copy()
        long["country_key"] = long["country_raw"].map(COUNTRY_KEY)
        long["country"] = long["country_key"].map(COUNTRY_LABEL)
        long["source"] = "Eurostat"
        long["source_url"] = eurostat_url(spec)
        long["indicator_id"] = spec["indicator_id"]
        long["indicator_label"] = spec["label"]
        long["theme"] = spec["theme"]
        long["unit"] = spec["unit"]
        long["bad_when"] = spec["bad_when"]
        long["note"] = spec["note"]
        frames.append(
            long[
                [
                    "source",
                    "source_url",
                    "indicator_id",
                    "indicator_label",
                    "theme",
                    "unit",
                    "bad_when",
                    "note",
                    "country_raw",
                    "country_key",
                    "country",
                    "year",
                    "value",
                ]
            ]
        )

    return pd.concat(frames, ignore_index=True)


def add_derived_indicators(panel: pd.DataFrame) -> pd.DataFrame:
    """Add normalized indicators that are more meaningful than raw country-size totals."""
    derived_frames: list[pd.DataFrame] = []

    patents = panel[panel["indicator_id"] == "IP.PAT.RESD"][
        ["country_raw", "country_key", "country", "year", "value"]
    ].rename(columns={"value": "patents"})
    population = panel[panel["indicator_id"] == "SP.POP.TOTL"][
        ["country_key", "year", "value"]
    ].rename(columns={"value": "population"})

    merged = patents.merge(population, on=["country_key", "year"], how="inner")
    merged = merged[(merged["population"] > 0) & merged["patents"].notna()].copy()
    if not merged.empty:
        merged["value"] = merged["patents"] / merged["population"] * 1_000_000
        merged["source"] = "World Bank WDI - elaborazione Nazareno Lecis"
        merged["source_url"] = (
            world_bank_url("IP.PAT.RESD") + " + " + world_bank_url("SP.POP.TOTL")
        )
        merged["indicator_id"] = "DERIVED_PATENTS_PER_MILLION"
        merged["indicator_label"] = "Domande di brevetto residenti per milione di abitanti"
        merged["theme"] = "innovazione"
        merged["unit"] = "brevetti per milione"
        merged["bad_when"] = "low"
        merged["note"] = "Indicatore derivato: brevetti residenti divisi per popolazione totale."
        derived_frames.append(merged)

    tourism = panel[panel["indicator_id"] == "ST.INT.ARVL"][
        ["country_raw", "country_key", "country", "year", "value"]
    ].rename(columns={"value": "tourist_arrivals"})
    tourism = tourism.merge(population, on=["country_key", "year"], how="inner")
    tourism = tourism[(tourism["population"] > 0) & tourism["tourist_arrivals"].notna()].copy()
    if not tourism.empty:
        tourism["value"] = tourism["tourist_arrivals"] / tourism["population"] * 1_000
        tourism["source"] = "World Bank WDI - elaborazione Nazareno Lecis"
        tourism["source_url"] = (
            world_bank_url("ST.INT.ARVL") + " + " + world_bank_url("SP.POP.TOTL")
        )
        tourism["indicator_id"] = "DERIVED_TOURISM_PER_1000"
        tourism["indicator_label"] = "Arrivi turistici internazionali per 1.000 abitanti"
        tourism["theme"] = "risparmio_turismo"
        tourism["unit"] = "arrivi per 1.000 abitanti"
        tourism["bad_when"] = "context"
        tourism["note"] = "Indicatore derivato: arrivi turistici internazionali divisi per popolazione totale."
        derived_frames.append(tourism)

    if not derived_frames:
        return panel

    keep = [
        "source",
        "source_url",
        "indicator_id",
        "indicator_label",
        "theme",
        "unit",
        "bad_when",
        "note",
        "country_raw",
        "country_key",
        "country",
        "year",
        "value",
    ]
    derived = pd.concat([frame[keep] for frame in derived_frames], ignore_index=True)
    return pd.concat([panel, derived], ignore_index=True)


def add_long_run_transforms(panel: pd.DataFrame, baseline_year: int = 2000, window: int = 10) -> pd.DataFrame:
    rows = []
    for (indicator_id, country_key), sub in panel.groupby(["indicator_id", "country_key"], sort=False):
        sub = sub.dropna(subset=["value"]).sort_values("year").copy()
        if sub.empty:
            continue

        baseline = first_from_year(sub, start_year=baseline_year)
        baseline_value = float(baseline["value"]) if baseline is not None else float("nan")
        sub["lag_value"] = sub["value"].shift(window)
        sub["lag_year"] = sub["year"].shift(window)

        for _, row in sub.iterrows():
            value = float(row["value"])
            lag_value = row["lag_value"]
            index_baseline = (
                100 * value / baseline_value
                if pd.notna(baseline_value) and baseline_value > 0 and value >= 0
                else float("nan")
            )
            growth_10y = (
                ((value / float(lag_value)) ** (1 / window) - 1) * 100
                if pd.notna(lag_value) and float(lag_value) > 0 and value > 0
                else float("nan")
            )
            rows.append(
                {
                    "indicator_id": indicator_id,
                    "indicator_label": row["indicator_label"],
                    "theme": row["theme"],
                    "country_key": country_key,
                    "country": row["country"],
                    "year": int(row["year"]),
                    "value": value,
                    "index_from_baseline": index_baseline,
                    "baseline_year": int(baseline["year"]) if baseline is not None else None,
                    "growth_10y_annualized_pct": growth_10y,
                    "window_years": window,
                }
            )
    return pd.DataFrame(rows)


def build_indicator_panel(refresh: bool = False, start_year: int = 1995) -> pd.DataFrame:
    _ = refresh
    wb = fetch_world_bank_panel(start_year=start_year)
    eurostat_panel = fetch_eurostat_productivity_panel(start_year=start_year)
    panel = pd.concat([wb, eurostat_panel], ignore_index=True)
    panel = add_derived_indicators(panel)
    return panel.sort_values(["theme", "indicator_label", "country_key", "year"]).reset_index(drop=True)


def first_from_year(df: pd.DataFrame, start_year: int = 2000) -> pd.Series | None:
    sub = df[df["year"] >= start_year].sort_values("year")
    if sub.empty:
        sub = df.sort_values("year")
    if sub.empty:
        return None
    return sub.iloc[0]


def latest(df: pd.DataFrame) -> pd.Series | None:
    sub = df.dropna(subset=["value"]).sort_values("year")
    if sub.empty:
        return None
    return sub.iloc[-1]


def summarize_decline(panel: pd.DataFrame, baseline_year: int = 2000) -> pd.DataFrame:
    rows = []
    for indicator_id, sub in panel.groupby("indicator_id", sort=False):
        italy = sub[sub["country_key"] == "ITA"]
        base = first_from_year(italy, start_year=baseline_year)
        last = latest(italy)
        if base is None or last is None:
            continue

        latest_year = int(last["year"])
        peers_latest = []
        for peer in PEER_KEYS:
            peer_last = latest(sub[(sub["country_key"] == peer) & (sub["year"] <= latest_year)])
            if peer_last is not None:
                peers_latest.append(float(peer_last["value"]))
        peer_mean = sum(peers_latest) / len(peers_latest) if peers_latest else float("nan")

        bad_when = str(last["bad_when"])
        change_abs = float(last["value"]) - float(base["value"])
        change_pct = change_abs / abs(float(base["value"])) * 100 if float(base["value"]) != 0 else float("nan")
        gap_vs_peer_mean = float(last["value"]) - peer_mean if pd.notna(peer_mean) else float("nan")

        if bad_when == "high":
            worsened_since_baseline = change_abs > 0
            italy_worse_than_peer_avg = gap_vs_peer_mean > 0 if pd.notna(gap_vs_peer_mean) else False
            bad_gap = gap_vs_peer_mean
        elif bad_when == "low":
            worsened_since_baseline = change_abs < 0
            italy_worse_than_peer_avg = gap_vs_peer_mean < 0 if pd.notna(gap_vs_peer_mean) else False
            bad_gap = -gap_vs_peer_mean if pd.notna(gap_vs_peer_mean) else float("nan")
        else:
            worsened_since_baseline = False
            italy_worse_than_peer_avg = False
            bad_gap = float("nan")

        rows.append(
            {
                "theme": last["theme"],
                "indicator_id": indicator_id,
                "indicator_label": last["indicator_label"],
                "unit": last["unit"],
                "source": last["source"],
                "bad_when": bad_when,
                "baseline_year": int(base["year"]),
                "baseline_value_italy": float(base["value"]),
                "latest_year": latest_year,
                "latest_value_italy": float(last["value"]),
                "change_abs_since_baseline": change_abs,
                "change_pct_since_baseline": change_pct,
                "peer_latest_mean": peer_mean,
                "gap_vs_peer_mean": gap_vs_peer_mean,
                "bad_gap_vs_peer_mean": bad_gap,
                "worsened_since_baseline": bool(worsened_since_baseline),
                "italy_worse_than_peer_avg": bool(italy_worse_than_peer_avg),
                "note": last["note"],
                "source_url": last["source_url"],
            }
        )
    summary = pd.DataFrame(rows)
    return summary.sort_values(["theme", "italy_worse_than_peer_avg", "worsened_since_baseline"], ascending=[True, False, False])


def plot_indicator(panel: pd.DataFrame, indicator_id: str, outdir: Path = PLOTS_DIR) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    sub = panel[panel["indicator_id"] == indicator_id].copy()
    if sub.empty:
        raise ValueError(f"Indicatore non trovato: {indicator_id}")

    label = sub["indicator_label"].iloc[0]
    unit = sub["unit"].iloc[0]
    source = sub["source"].iloc[0]

    fig, ax = plt.subplots(figsize=(9, 5))
    n_countries = sub["country_key"].nunique()

    if n_countries > 8 and "ITA" in set(sub["country_key"]):
        pivot = sub.pivot_table(index="year", columns="country_key", values="value", aggfunc="mean").sort_index()
        country_cols = [c for c in pivot.columns if c != "EU"]
        advanced = pivot[country_cols]
        years = pivot.index.to_numpy()
        ax.fill_between(years, advanced.min(axis=1), advanced.max(axis=1), color="#eeeeee", label="Minimo-massimo paesi avanzati")
        ax.fill_between(years, advanced.quantile(0.25, axis=1), advanced.quantile(0.75, axis=1), color="#bdbdbd", label="Pct 25-75")
        ax.plot(years, advanced.median(axis=1), color="black", linestyle=(0, (4, 3)), linewidth=1.8, label="Mediana")
        ax.plot(years, pivot["ITA"], color="#0875c9", linewidth=3, label="Italia")
    else:
        for key, country_sub in sub.sort_values("year").groupby("country_key"):
            country_sub.plot(
                x="year",
                y="value",
                ax=ax,
                label=COUNTRY_LABEL.get(key, key),
                linewidth=2.6 if key == "ITA" else 1.4,
            )
    ax.set_title(label)
    ax.set_xlabel("Anno")
    ax.set_ylabel(unit)
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=2)
    credit = source if "elaborazione" in source.lower() else f"{source} - elaborazione Nazareno Lecis"
    fig.text(0.01, 0.01, f"Fonte: {credit}", ha="left", fontsize=8)
    plt.tight_layout(rect=[0, 0.04, 1, 1])

    out = outdir / f"{slugify(indicator_id)}_{slugify(label)}.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def save_key_plots(
    panel: pd.DataFrame,
    indicator_ids: Iterable[str] = IMPORTANT_PLOT_INDICATORS,
) -> list[Path]:
    available = set(panel["indicator_id"].drop_duplicates())
    return [plot_indicator(panel, indicator_id) for indicator_id in indicator_ids if indicator_id in available]


def build_snapshot(summary: pd.DataFrame) -> str:
    flagged = summary[(summary["italy_worse_than_peer_avg"]) | (summary["worsened_since_baseline"])].copy()
    flagged = flagged.sort_values(["theme", "bad_gap_vs_peer_mean"], ascending=[True, False])

    lines = [
        "# Snapshot declino Italia",
        "",
        "Indicatori ufficiali via API World Bank ed Eurostat. La colonna `bad_when` indica la direzione interpretativa usata nei gap: `low` significa che valori piu bassi sono peggiori, `high` significa che valori piu alti sono peggiori.",
        "",
        "## Indicatori critici",
        "",
    ]
    if flagged.empty:
        lines.append("Nessun indicatore risulta simultaneamente peggiorato o sotto la media dei peer con i dati disponibili.")
    else:
        for _, row in flagged.iterrows():
            lines.append(
                f"- **{row['indicator_label']}** ({row['theme']}): Italia {row['latest_value_italy']:.2f} "
                f"nel {int(row['latest_year'])}; variazione dal {int(row['baseline_year'])}: "
                f"{row['change_abs_since_baseline']:.2f}; gap vs media peer: {row['gap_vs_peer_mean']:.2f}."
            )

    lines.extend(
        [
            "",
            "## Output",
            "",
            "- Tabelle in memoria: panel, summary, transforms.",
            "- Grafici PNG nella cartella del codice che li genera.",
        ]
    )
    return "\n".join(lines)


def run_decline_analysis(
    refresh: bool = False,
    start_year: int = 1995,
    plot_indicators: Iterable[str] | None = IMPORTANT_PLOT_INDICATORS,
) -> dict[str, object]:
    panel = build_indicator_panel(refresh=refresh, start_year=start_year)
    summary = summarize_decline(panel)
    transforms = add_long_run_transforms(panel)
    plot_paths = save_key_plots(panel, plot_indicators) if plot_indicators is not None else []
    snapshot = build_snapshot(summary)
    return {
        "panel": panel,
        "summary": summary,
        "transforms": transforms,
        "plot_paths": plot_paths,
        "snapshot": snapshot,
    }


def main() -> None:
    result = run_decline_analysis(refresh=False)
    summary = result["summary"]
    print(summary[["theme", "indicator_label", "latest_year", "latest_value_italy", "gap_vs_peer_mean"]].to_string(index=False))
    print(f"[SAVED] Grafici: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
