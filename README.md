# ORA-Lab

Repository dedicata alle attività del team di ORA! Lab.

## Analisi disponibili

- `analisi/`: cartelle ordinate per argomento (`istruzione`, `ricerca`, `demografia`, `valore_aggiunto`, `occupazione`, `pil`).
- `fonti/verifica_fonti.py`: verifica accesso minimo a Eurostat, ISTAT, OECD ed ECB.
- `dati/istat/`: file Excel ISTAT grezzi.
- `analisi/pil/pil_lavoro.py`: indici trimestrali ISTAT di PIL, occupati, ore lavorate e produttivita implicita.
- `analisi/valore_aggiunto/valore_aggiunto_pil.py`: confronto settoriale tra valore aggiunto e ore lavorate.
- `analisi/_comune/indicatori_api.py`: funzioni API condivise; salva solo i grafici chiave.
- `notebooks/`: notebook commentati per esplorare i risultati.

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## Rigenerare output e grafici

```bash
python3 analisi/pil/pil_lavoro.py
python3 analisi/valore_aggiunto/valore_aggiunto_pil.py
python3 analisi/_comune/indicatori_api.py
python3 fonti/verifica_fonti.py
```

Gli output principali sono in:

- `analisi/pil/output/`
- `analisi/valore_aggiunto/output/`
- `analisi/_comune/output_indicatori/`

Per l'analisi API, i grafici principali sono in `analisi/_comune/output_indicatori/plots_key/`; il CSV completo resta disponibile per eventuali approfondimenti senza produrre decine di immagini.

## Notebook

- `notebooks/01_declino_italiano_dashboard_api.ipynb`
- `notebooks/02_produttivita_istat_pil_lavoro_settori.ipynb`
- `notebooks/03_demografia_natalita_innovazione_burocrazia.ipynb`

I notebook usano i CSV salvati quando possibile. Per riscaricare le API, impostare `REFRESH_API = True` nelle prime celle.

## Fonti

- ISTAT: file Excel inclusi nella cartella `dati/istat/`.
- World Bank API: World Development Indicators, Worldwide Governance Indicators e Doing Business storico.
- Eurostat API: `nama_10_lp_ulc` per produttivita reale, ore lavorate e costo del lavoro per unita di prodotto.
