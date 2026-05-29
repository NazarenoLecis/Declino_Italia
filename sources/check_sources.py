from __future__ import annotations

import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sources.api_catalog import FONTI_API, FonteApi


def controlla_fonte_api(fonte: FonteApi) -> dict[str, object]:
    headers = {"Accept": fonte.accept, "User-Agent": "Nazareno-Lecis-Declino-Italia/1.0"}
    try:
        with requests.get(fonte.url_controllo, headers=headers, timeout=fonte.timeout, stream=True) as response:
            preview = response.raw.read(300, decode_content=True)
            return {
                "fonte": fonte.nome,
                "ente": fonte.ente,
                "obbligatoria": fonte.obbligatoria,
                "ok": response.ok and len(preview) > 0,
                "status": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "bytes_read": len(preview),
                "url": fonte.url_controllo,
            }
    except Exception as exc:
        return {
            "fonte": fonte.nome,
            "ente": fonte.ente,
            "obbligatoria": fonte.obbligatoria,
            "ok": False,
            "status": "error",
            "content_type": "",
            "bytes_read": 0,
            "error": repr(exc),
            "url": fonte.url_controllo,
        }


def controlla_tutte_le_fonti() -> list[dict[str, object]]:
    return [controlla_fonte_api(fonte) for fonte in FONTI_API]


def main() -> None:
    risultati = controlla_tutte_le_fonti()
    for row in risultati:
        status = "OK" if row["ok"] else "NO"
        obbligo = "core" if row["obbligatoria"] else "da_mappare"
        print(
            f"{status} | {obbligo} | {row['fonte']} | {row['ente']} | "
            f"status={row['status']} | byte={row['bytes_read']} | {row['content_type']}"
        )

    if not all(row["ok"] for row in risultati if row["obbligatoria"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
