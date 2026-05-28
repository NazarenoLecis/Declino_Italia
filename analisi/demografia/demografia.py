from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from analisi._comune.indicatori_api import build_indicator_panel, plot_indicator, summarize_decline


BASE_DIR = Path(__file__).resolve().parent
OUTDIR = BASE_DIR / "output"
OUTDIR.mkdir(exist_ok=True)

TEMI = ["demografia", "natalita"]
GRAFICI = ["SP.DYN.TFRT.IN", "SP.DYN.CBRT.IN", "SP.POP.65UP.TO.ZS", "SP.POP.GROW"]


def esegui(refresh: bool = False) -> None:
    panel = build_indicator_panel(refresh=refresh)
    panel_tema = panel[panel["theme"].isin(TEMI)].copy()
    summary = summarize_decline(panel_tema)

    panel_tema.to_csv(OUTDIR / "demografia_panel.csv", index=False, encoding="utf-8")
    summary.to_csv(OUTDIR / "demografia_summary.csv", index=False, encoding="utf-8")
    for indicatore in GRAFICI:
        plot_indicator(panel, indicatore, OUTDIR)


if __name__ == "__main__":
    esegui(refresh=False)
