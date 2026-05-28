# Declino Italia

Repository personale di analisi sul declino economico e sociale italiano. Le analisi usano solo API pubbliche: non sono previsti file Excel, CSV o dataset manuali come input. Le tabelle restano in memoria nei notebook e negli script; i grafici vengono mostrati nei notebook e, quando salvati come PNG, restano file locali ignorati da Git.

Tutti i grafici riportano la fonte e la dicitura `elaborazione Nazareno Lecis`.

## Fonti

Fonti gia collegate:

- World Bank API: WDI, WGI e Doing Business storico.
- Eurostat API: produttivita reale, costo del lavoro per unita di prodotto e ore lavorate.

Fonti da collegare per completare alcuni grafici:

- ISTAT API: migrazioni, eta, sesso, lavoro di dettaglio.
- UN WPP API: fasce demografiche non disponibili in WDI.
- OECD API: R&S per finanziatore/settore, ore, produttivita e alcune serie congiunturali.
- DG ECFIN/AMECO API: PIL potenziale, TFP, NAWRU e variabili strutturali.
- API elettorali ufficiali o equivalenti: partecipazione al voto e indicatori politici.

Gli endpoint gia disponibili si verificano con:

```bash
python3 sources/check_sources.py
```

## Struttura

- `analisi/cruscotto/`: vista trasversale degli indicatori principali del progetto.
- `analisi/pil/`: PIL reale e nominale, PIL pro capite, produttivita, crescita media e crescita cumulata.
- `analisi/valore_aggiunto/`: valore aggiunto industriale e manifatturiero.
- `analisi/demografia/`: popolazione, fasce di eta, natalita, fertilita, dipendenze, migrazioni e aspettativa di vita.
- `analisi/occupazione/`: forze lavoro, occupazione, disoccupazione, ore lavorate e indicatori del mercato del lavoro.
- `analisi/istruzione/`: capitale umano e iscrizione terziaria.
- `analisi/ricerca/`: R&S, brevetti, export high-tech e indicatori di innovazione.
- `analisi/istituzioni/`: burocrazia, governance, qualita regolatoria e indicatori istituzionali.
- `analisi/utils/`: funzioni condivise per scaricare dati API, trasformarli e disegnare grafici comparabili.
- `sources/`: controlli rapidi sugli endpoint API.

## Notebook

Notebook principali gia presenti:

- `analisi/cruscotto/notebooks/00_declino_italiano_dashboard_api.ipynb`
- `analisi/pil/notebooks/01_produttivita_reddito_api.ipynb`
- `analisi/demografia/notebooks/01_demografia_natalita_api.ipynb`
- `analisi/istruzione/notebooks/01_capitale_umano_api.ipynb`
- `analisi/ricerca/notebooks/01_innovazione_api.ipynb`
- `analisi/istituzioni/notebooks/01_burocrazia_istituzioni_api.ipynb`

Notebook dei grafici:

- `analisi/pil/notebooks/02_grafici_pil_produttivita_api.ipynb`
- `analisi/valore_aggiunto/notebooks/01_grafici_valore_aggiunto_api.ipynb`
- `analisi/demografia/notebooks/02_grafici_demografia_api.ipynb`
- `analisi/occupazione/notebooks/01_grafici_occupazione_api.ipynb`
- `analisi/ricerca/notebooks/02_grafici_ricerca_api.ipynb`
- `analisi/istituzioni/notebooks/02_grafici_istituzioni_api.ipynb`

Nei notebook dei grafici sono definite le specifiche della singola categoria: indicatori, trasformazioni, pagine di riferimento, fonte e nome dell'output. Le funzioni generali stanno invece in `analisi/utils/grafici.py`: download API, trasformazioni ricorrenti, confronto con la distribuzione dei paesi avanzati e salvataggio PNG.

Ogni notebook mostra:

- l'inventario dei grafici della categoria;
- i PNG generati con le API gia mappate;
- i grafici in attesa di mapping API specifico, senza introdurre input manuali.

## Output

I grafici vengono visualizzati nei notebook. Quando una cella salva PNG di appoggio, i file vengono creati nella cartella della categoria ma non vengono versionati:

- `analisi/pil/*.png`
- `analisi/valore_aggiunto/*.png`
- `analisi/demografia/*.png`
- `analisi/occupazione/*.png`
- `analisi/ricerca/*.png`
- `analisi/istituzioni/*.png`, quando le relative API saranno collegate

Non vengono versionati PNG, CSV o Excel.

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

Oppure apri un notebook in `analisi/<categoria>/notebooks/` ed esegui le celle. I notebook dei grafici salvano i grafici nella cartella della categoria e mantengono le tabelle solo in memoria.
