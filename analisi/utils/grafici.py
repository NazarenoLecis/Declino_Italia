from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import requests


PAESI_AVANZATI = [
    "ITA",
    "DEU",
    "FRA",
    "ESP",
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

PAESI_MONDO = PAESI_AVANZATI + ["WLD"]

ETICHETTE_PAESE = {
    "ITA": "Italia",
    "DEU": "Germania",
    "FRA": "Francia",
    "ESP": "Spagna",
    "USA": "Stati Uniti",
    "JPN": "Giappone",
    "GBR": "Regno Unito",
    "CAN": "Canada",
    "AUS": "Australia",
    "AUT": "Austria",
    "BEL": "Belgio",
    "CHE": "Svizzera",
    "DNK": "Danimarca",
    "FIN": "Finlandia",
    "NLD": "Paesi Bassi",
    "NOR": "Norvegia",
    "SWE": "Svezia",
    "PRT": "Portogallo",
    "GRC": "Grecia",
    "IRL": "Irlanda",
    "WLD": "Mondo",
}

FIRMA_FONTE = "elaborazione Nazareno Lecis"


@dataclass(frozen=True)
class SpecificaGrafico:
    pagine: str
    sezione: str
    titolo: str
    nome_output: str
    fonte: str
    tipo: str
    indicatore: str | None = None
    numeratore: str | None = None
    denominatore: str | None = None
    scala: float = 1.0
    operazione: str = "ratio"
    anno_base: int = 1970
    finestra: int = 10
    paesi: tuple[str, ...] = tuple(PAESI_AVANZATI)
    confronto: bool = True
    note: str = ""
    supportato: bool = True


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def world_bank_url(indicator: str, countries: Iterable[str]) -> str:
    country_path = ";".join(countries)
    return f"https://api.worldbank.org/v2/country/{country_path}/indicator/{indicator}"


def scarica_indicatore_world_bank(indicator: str, countries: Iterable[str], start_year: int = 1960) -> pd.DataFrame:
    countries = list(countries)
    response = requests.get(
        world_bank_url(indicator, countries),
        params={"format": "json", "per_page": 20000},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Risposta World Bank inattesa per {indicator}")

    rows = []
    for item in payload[1] or []:
        value = item.get("value")
        if value is None:
            continue
        year = int(item["date"])
        if year < start_year:
            continue
        country = item.get("countryiso3code") or item.get("country", {}).get("id")
        rows.append(
            {
                "country_key": country,
                "country": ETICHETTE_PAESE.get(country, item.get("country", {}).get("value", country)),
                "year": year,
                "value": float(value),
                "source_url": response.url,
            }
        )
    return pd.DataFrame(rows)


def scarica_valori_specifica(spec: SpecificaGrafico, start_year: int = 1960) -> pd.DataFrame:
    if not spec.supportato:
        raise ValueError(f"Grafico non supportato: {spec.titolo}")

    countries = spec.paesi
    if spec.numeratore is not None and spec.denominatore is not None:
        if spec.numeratore is None or spec.denominatore is None:
            raise ValueError(f"Ratio incompleto: {spec.titolo}")
        num = scarica_indicatore_world_bank(spec.numeratore, countries, start_year).rename(columns={"value": "numerator"})
        den = scarica_indicatore_world_bank(spec.denominatore, countries, start_year).rename(columns={"value": "denominator"})
        merged = num.merge(den[["country_key", "year", "denominator"]], on=["country_key", "year"], how="inner")
        merged = merged[merged["numerator"].notna() & merged["denominator"].notna()].copy()
        if spec.operazione == "product":
            merged["value"] = merged["numerator"] * merged["denominator"] * spec.scala
        else:
            merged = merged[merged["denominator"] != 0].copy()
            merged["value"] = merged["numerator"] / merged["denominator"] * spec.scala
        return merged[["country_key", "country", "year", "value", "source_url"]]

    if spec.indicatore is None:
        raise ValueError(f"Indicatore mancante: {spec.titolo}")
    return scarica_indicatore_world_bank(spec.indicatore, countries, start_year)


def crescita_annualizzata(values: pd.Series, window: int) -> pd.Series:
    lag = values.shift(window)
    out = ((values / lag) ** (1 / window) - 1) * 100
    return out.where((values > 0) & (lag > 0))


def trasforma_valori(df: pd.DataFrame, spec: SpecificaGrafico) -> pd.DataFrame:
    frames = []
    for _, sub in df.sort_values("year").groupby("country_key", sort=False):
        sub = sub.copy()
        if spec.tipo in {"level", "ratio"}:
            sub["plot_value"] = sub["value"]
        elif spec.tipo == "growth_10y":
            sub["plot_value"] = crescita_annualizzata(sub["value"], spec.finestra)
        elif spec.tipo == "index":
            base = sub[sub["year"] >= spec.anno_base].sort_values("year")
            if base.empty or base.iloc[0]["value"] == 0:
                sub["plot_value"] = math.nan
            else:
                sub["plot_value"] = sub["value"] / float(base.iloc[0]["value"]) * 100
        elif spec.tipo == "share_world":
            frames.append(sub)
            continue
        else:
            raise ValueError(f"Trasformazione sconosciuta: {spec.tipo}")
        frames.append(sub)

    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if spec.tipo == "share_world":
        pivot = out.pivot_table(index="year", columns="country_key", values="value", aggfunc="mean")
        if "ITA" not in pivot or "WLD" not in pivot:
            return pd.DataFrame()
        share = (pivot["ITA"] / pivot["WLD"] * 100).dropna().reset_index(name="plot_value")
        share["country_key"] = "ITA"
        share["country"] = "Italia"
        return share

    return out.dropna(subset=["plot_value"])


def disegna_distribuzione(df: pd.DataFrame, spec: SpecificaGrafico, outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    pivot = df.pivot_table(index="year", columns="country_key", values="plot_value", aggfunc="mean").sort_index()

    if spec.confronto and "ITA" in pivot and len(pivot.columns) > 5:
        peers = pivot[[c for c in pivot.columns if c != "WLD"]]
        years = peers.index.to_numpy()
        ax.fill_between(years, peers.min(axis=1), peers.max(axis=1), color="#eeeeee", label="Minimo-massimo paesi avanzati")
        ax.fill_between(years, peers.quantile(0.25, axis=1), peers.quantile(0.75, axis=1), color="#bdbdbd", label="Pct 25-75")
        ax.plot(years, peers.median(axis=1), color="black", linestyle=(0, (4, 3)), linewidth=1.8, label="Mediana")
        ax.plot(years, pivot["ITA"], color="#0875c9", linewidth=3, label="Italia")
    else:
        for country_key in pivot.columns:
            ax.plot(
                pivot.index,
                pivot[country_key],
                linewidth=3 if country_key == "ITA" else 1.6,
                label=ETICHETTE_PAESE.get(country_key, country_key),
            )

    ax.set_title(spec.titolo)
    ax.set_xlabel("Anno")
    ax.set_ylabel(etichetta_asse_y(spec))
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=2)
    fig.text(0.01, 0.01, f"Fonte: {spec.fonte} - {FIRMA_FONTE}", ha="left", fontsize=8)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out = outdir / f"{spec.nome_output}.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def etichetta_asse_y(spec: SpecificaGrafico) -> str:
    if spec.tipo == "growth_10y":
        return "% annuo"
    if spec.tipo == "index":
        return f"indice {spec.anno_base}=100"
    if spec.tipo == "share_world":
        return "% PIL mondiale"
    if spec.nome_output.endswith("_quota") or "% del" in spec.titolo:
        return "%"
    return "livello"


def genera_grafico(spec: SpecificaGrafico, outdir: Path, start_year: int = 1960) -> Path:
    values = scarica_valori_specifica(spec, start_year=start_year)
    transformed = trasforma_valori(values, spec)
    if transformed.empty:
        raise RuntimeError(f"Nessun dato disponibile per {spec.titolo}")
    return disegna_distribuzione(transformed, spec, outdir)


def genera_grafici_supportati(specifiche: Iterable[SpecificaGrafico], outdir: Path, start_year: int = 1960) -> tuple[list[Path], pd.DataFrame]:
    paths: list[Path] = []
    rows = []
    for spec in specifiche:
        stato = "supportato" if spec.supportato else "in_attesa_mapping_api"
        errore = ""
        if spec.supportato:
            try:
                paths.append(genera_grafico(spec, outdir, start_year=start_year))
                stato = "generato"
            except Exception as exc:  # I notebook devono mostrare gli errori API senza nascondere l'inventario.
                stato = "errore"
                errore = str(exc)
        rows.append(
            {
                "pagine": spec.pagine,
                "sezione": spec.sezione,
                "titolo": spec.titolo,
                "fonte": spec.fonte,
                "stato": stato,
                "nome_output": spec.nome_output,
                "note": spec.note,
                "errore": errore,
            }
        )
    return paths, pd.DataFrame(rows)


def specifica_world_bank(
    sezione: str,
    pagine: str,
    titolo: str,
    nome_output: str,
    indicatore: str,
    tipo: str,
    fonte: str = "World Bank API",
    confronto: bool = True,
    paesi: tuple[str, ...] = tuple(PAESI_AVANZATI),
    anno_base: int = 1970,
    note: str = "",
) -> SpecificaGrafico:
    return SpecificaGrafico(
        pagine=pagine,
        sezione=sezione,
        titolo=titolo,
        nome_output=nome_output,
        fonte=fonte,
        tipo=tipo,
        indicatore=indicatore,
        confronto=confronto,
        paesi=paesi,
        anno_base=anno_base,
        note=note,
    )


def specifica_rapporto(
    sezione: str,
    pagine: str,
    titolo: str,
    nome_output: str,
    numeratore: str,
    denominatore: str,
    scala: float,
    tipo: str = "ratio",
    fonte: str = "World Bank API",
    confronto: bool = True,
    paesi: tuple[str, ...] = tuple(PAESI_AVANZATI),
    anno_base: int = 1970,
    operazione: str = "ratio",
) -> SpecificaGrafico:
    return SpecificaGrafico(
        pagine=pagine,
        sezione=sezione,
        titolo=titolo,
        nome_output=nome_output,
        fonte=fonte,
        tipo=tipo,
        numeratore=numeratore,
        denominatore=denominatore,
        scala=scala,
        operazione=operazione,
        confronto=confronto,
        paesi=paesi,
        anno_base=anno_base,
    )


def specifica_in_attesa(sezione: str, pagine: str, titolo: str, nome_output: str, fonte: str, note: str) -> SpecificaGrafico:
    return SpecificaGrafico(
        pagine=pagine,
        sezione=sezione,
        titolo=titolo,
        nome_output=nome_output,
        fonte=fonte,
        tipo="pending",
        supportato=False,
        note=note,
    )
