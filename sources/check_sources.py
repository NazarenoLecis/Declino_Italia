from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    accept: str = "application/json, */*"
    timeout: int = 20


SOURCES = [
    Source(
        "Eurostat",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_lp_ulc"
        "?format=JSON&lang=en&freq=A&unit=I15&na_item=RLPR_HW&geo=IT&time=2023",
    ),
    Source(
        "ISTAT",
        "https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/all/latest",
    ),
    Source(
        "OECD",
        "https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest",
        timeout=60,
    ),
    Source(
        "ECB",
        "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1",
        "application/vnd.sdmx.genericdata+xml, */*",
    ),
]


def check_source(source: Source) -> dict[str, object]:
    headers = {"Accept": source.accept, "User-Agent": "Nazareno-Lecis-Declino-Italia/1.0"}
    try:
        with requests.get(source.url, headers=headers, timeout=source.timeout, stream=True) as response:
            preview = response.raw.read(300, decode_content=True)
            return {
                "source": source.name,
                "ok": response.ok and len(preview) > 0,
                "status": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "bytes_read": len(preview),
                "url": source.url,
            }
    except Exception as exc:
        return {
            "source": source.name,
            "ok": False,
            "status": "error",
            "content_type": "",
            "bytes_read": 0,
            "error": repr(exc),
            "url": source.url,
        }


def check_all_sources() -> list[dict[str, object]]:
    return [check_source(source) for source in SOURCES]


def main() -> None:
    results = check_all_sources()
    for row in results:
        status = "OK" if row["ok"] else "NO"
        print(f"{status} | {row['source']} | status={row['status']} | byte={row['bytes_read']} | {row['content_type']}")

    if not all(row["ok"] for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
