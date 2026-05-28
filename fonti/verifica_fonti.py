from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class Fonte:
    nome: str
    url: str
    accept: str = "application/json, */*"
    timeout: int = 20


FONTI = [
    Fonte(
        "Eurostat",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_lp_ulc"
        "?format=JSON&lang=en&freq=A&unit=I15&na_item=RLPR_HW&geo=IT&time=2023",
    ),
    Fonte(
        "ISTAT",
        "https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/all/latest",
    ),
    Fonte(
        "OECD",
        "https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest",
        timeout=60,
    ),
    Fonte(
        "ECB",
        "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1",
        "application/vnd.sdmx.genericdata+xml, */*",
    ),
]


def verifica_fonte(fonte: Fonte) -> dict[str, object]:
    headers = {"Accept": fonte.accept, "User-Agent": "ORA-Lab/1.0"}
    try:
        with requests.get(fonte.url, headers=headers, timeout=fonte.timeout, stream=True) as response:
            anteprima = response.raw.read(300, decode_content=True)
            return {
                "fonte": fonte.nome,
                "ok": response.ok and len(anteprima) > 0,
                "status": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "byte_letti": len(anteprima),
                "url": fonte.url,
            }
    except Exception as exc:
        return {
            "fonte": fonte.nome,
            "ok": False,
            "status": "errore",
            "content_type": "",
            "byte_letti": 0,
            "errore": repr(exc),
            "url": fonte.url,
        }


def verifica_tutte_le_fonti() -> list[dict[str, object]]:
    return [verifica_fonte(fonte) for fonte in FONTI]


def main() -> None:
    risultati = verifica_tutte_le_fonti()
    for riga in risultati:
        stato = "OK" if riga["ok"] else "NO"
        print(f"{stato} | {riga['fonte']} | status={riga['status']} | byte={riga['byte_letti']} | {riga['content_type']}")

    if not all(riga["ok"] for riga in risultati):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
