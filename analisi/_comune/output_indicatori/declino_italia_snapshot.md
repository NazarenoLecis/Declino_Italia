# Snapshot declino Italia

Indicatori ufficiali via API World Bank ed Eurostat. La colonna `bad_when` indica la direzione interpretativa usata nei gap: `low` significa che valori piu bassi sono peggiori, `high` significa che valori piu alti sono peggiori.

## Indicatori critici

- **Tempo per adempimenti fiscali** (burocrazia): Italia 238.00 nel 2019; variazione dal 2005: -102.00; gap vs media peer: 71.33.
- **Carico fiscale totale sulle imprese** (burocrazia): Italia 59.10 nel 2019; variazione dal 2005: -17.60; gap vs media peer: 6.93.
- **Tempo per avviare una impresa** (burocrazia): Italia 11.00 nel 2019; variazione dal 2003: -12.00; gap vs media peer: 2.83.
- **Iscrizione terziaria lorda** (capitale_umano): Italia 75.95 nel 2023; variazione dal 2001: 22.50; gap vs media peer: -4.62.
- **Popolazione 65+** (demografia): Italia 24.62 nel 2024; variazione dal 2000: 6.41; gap vs media peer: 2.50.
- **Crescita della popolazione** (demografia): Italia -0.05 nel 2024; variazione dal 2000: -0.10; gap vs media peer: -0.52.
- **Popolazione in eta 15-64** (demografia): Italia 63.48 nel 2024; variazione dal 2000: -4.03; gap vs media peer: 0.05.
- **Interessi sul debito** (finanza_pubblica): Italia 9.42 nel 2024; variazione dal 2000: -6.82; gap vs media peer: 5.38.
- **Domande di brevetto residenti per milione di abitanti** (innovazione): Italia 173.86 nel 2021; variazione dal 2000: 35.53; gap vs media peer: -60.65.
- **Export high-tech** (innovazione): Italia 12.28 nel 2024; variazione dal 2007: 5.55; gap vs media peer: -5.47.
- **Spesa in R&S** (innovazione): Italia 1.38 nel 2023; variazione dal 2000: 0.38; gap vs media peer: -0.89.
- **Crescita investimenti fissi reali** (investimenti): Italia 0.47 nel 2024; variazione dal 2000: -6.44; gap vs media peer: 1.11.
- **Crescita formazione lorda di capitale reale** (investimenti): Italia 0.29 nel 2024; variazione dal 2000: -5.39; gap vs media peer: 1.55.
- **Controllo della corruzione** (istituzioni): Italia 0.55 nel 2024; variazione dal 2000: -0.23; gap vs media peer: -0.68.
- **Stato di diritto** (istituzioni): Italia 0.62 nel 2024; variazione dal 2000: -0.26; gap vs media peer: -0.56.
- **Efficacia del governo** (istituzioni): Italia 0.79 nel 2024; variazione dal 2000: 0.04; gap vs media peer: -0.49.
- **Qualita regolatoria** (istituzioni): Italia 0.64 nel 2024; variazione dal 2000: -0.16; gap vs media peer: -0.45.
- **Natalita grezza** (natalita): Italia 6.30 nel 2024; variazione dal 2000: -3.20; gap vs media peer: -1.75.
- **Tasso di fertilita** (natalita): Italia 1.18 nel 2024; variazione dal 2000: -0.08; gap vs media peer: -0.17.
- **Crescita consumi privati reali** (prezzi_consumi): Italia 1.22 nel 2023; variazione dal 2000: -1.44; gap vs media peer: 0.72.
- **PIL reale pro capite** (produttivita_reddito): Italia 34495.25 nel 2024; variazione dal 2000: 1885.59; gap vs media peer: -2467.93.
- **Produttivita reale per ora lavorata** (produttivita_reddito): Italia 98.76 nel 2025; variazione dal 2000: -0.27; gap vs media peer: -5.78.
- **Produttivita reale per occupato** (produttivita_reddito): Italia 100.38 nel 2025; variazione dal 2000: -6.84; gap vs media peer: -1.41.
- **Crescita reale del PIL** (produttivita_reddito): Italia 0.69 nel 2024; variazione dal 2000: -3.19; gap vs media peer: -0.61.
- **Costo del lavoro per unita di prodotto** (produttivita_reddito): Italia 117.93 nel 2025; variazione dal 2000: 46.51; gap vs media peer: -12.28.
- **PIL per occupato** (produttivita_reddito): Italia 130388.07 nel 2024; variazione dal 2000: -7371.95; gap vs media peer: 11237.21.
- **Crescita valore aggiunto manifattura** (produzione): Italia -0.68 nel 2024; variazione dal 2000: -3.57; gap vs media peer: -0.64.
- **Crescita valore aggiunto industria** (produzione): Italia 0.28 nel 2024; variazione dal 2000: -2.62; gap vs media peer: 0.15.
- **Quota manifattura sul valore aggiunto** (produzione): Italia 14.82 nel 2024; variazione dal 2000: -2.85; gap vs media peer: 1.64.
- **Risparmio netto aggiustato** (risparmio_turismo): Italia 7.69 nel 2021; variazione dal 2000: -1.39; gap vs media peer: -3.14.
- **Risparmio nazionale lordo** (risparmio_turismo): Italia 23.65 nel 2024; variazione dal 2000: 2.60; gap vs media peer: -0.76.

## File generati

- `declino_italia_indicator_panel.csv`: serie annuali normalizzate.
- `declino_italia_indicator_summary.csv`: sintesi Italia, trend e gap.
- `declino_italia_indicator_transforms.csv`: indici da baseline e crescita decennale annualizzata.
- `plots_key/`: grafici selezionati sugli indicatori piu importanti.