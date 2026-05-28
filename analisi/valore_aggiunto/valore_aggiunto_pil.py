from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from analisi.utils.api_indicators import build_indicator_panel, plot_indicator, summarize_decline


BASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = BASE_DIR

THEMES = ["produzione"]
CHARTS = ["NV.IND.TOTL.KD.ZG", "NV.IND.MANF.KD.ZG", "NV.IND.MANF.ZS"]


def run(refresh: bool = False) -> None:
    panel = build_indicator_panel(refresh=refresh)
    theme_panel = panel[panel["theme"].isin(THEMES)].copy()
    summary = summarize_decline(theme_panel)

    for indicator_id in CHARTS:
        plot_indicator(panel, indicator_id, PLOTS_DIR)
    print(summary[["indicator_label", "latest_year", "latest_value_italy", "gap_vs_peer_mean"]].to_string(index=False))


if __name__ == "__main__":
    run(refresh=False)
