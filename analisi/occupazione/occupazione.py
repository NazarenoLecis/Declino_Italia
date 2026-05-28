from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from analisi.pil.pil_lavoro import carica_occupati_totali


BASE_DIR = Path(__file__).resolve().parent
OUTDIR = BASE_DIR / "output"
OUTDIR.mkdir(exist_ok=True)


def esegui() -> None:
    occupati = carica_occupati_totali().rename("occupati_migliaia").reset_index()
    occupati = occupati.rename(columns={"period": "trimestre"})
    occupati["trimestre"] = occupati["trimestre"].astype(str)
    occupati.to_csv(OUTDIR / "occupati_totali_trimestrali.csv", index=False, encoding="utf-8")

    ultimo_anno = (
        occupati.assign(anno=occupati["trimestre"].str[:4].astype(int))
        .groupby("anno", as_index=False)["occupati_migliaia"]
        .mean()
        .tail(10)
    )
    ultimo_anno.to_csv(OUTDIR / "occupati_totali_annuali_ultimi_10_anni.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    esegui()
