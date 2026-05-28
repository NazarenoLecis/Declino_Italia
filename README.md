# Declino Italia

Repository per analizzare, con dati ufficiali via API, alcune dimensioni del declino economico e sociale italiano: produttivita, demografia, capitale umano, innovazione, occupazione, struttura produttiva e istituzioni.

Il progetto non usa file Excel o dataset manuali come input. Le analisi interrogano direttamente API pubbliche e lavorano i dati in memoria; gli script possono salvare solo grafici PNG nella stessa cartella del codice che li genera.

## Fonti

Fonti attive:

- World Bank API: WDI, WGI e indicatori Doing Business storici.
- Eurostat API: produttivita reale, costo del lavoro per unita di prodotto e ore lavorate per occupato.

Endpoint verificabili:

```bash
python3 sources/check_sources.py
```

## Struttura

- `analisi/utils/`: funzioni condivise per scaricare indicatori, costruire pannelli in memoria, calcolare sintesi e generare grafici.
- `analisi/cruscotto/`: notebook trasversale sul quadro complessivo.
- `analisi/pil/`: PIL, produttivita aggregata, produttivita per ora e per occupato.
- `analisi/valore_aggiunto/`: produzione e valore aggiunto da indicatori API aggregati.
- `analisi/occupazione/`: occupazione, disoccupazione e forza lavoro.
- `analisi/demografia/`: popolazione, natalita, fertilita e invecchiamento.
- `analisi/istruzione/`: capitale umano e iscrizione terziaria.
- `analisi/ricerca/`: R&S, brevetti ed export high-tech.
- `analisi/istituzioni/`: burocrazia, governance e qualita regolatoria.
- `sources/`: verifica degli endpoint API.

## Uso

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

Esegui uno script tematico:

```bash
python3 analisi/pil/pil_lavoro.py
python3 analisi/demografia/demografia.py
python3 analisi/ricerca/ricerca.py
```

Oppure apri i notebook in `analisi/<categoria>/notebooks/`.
