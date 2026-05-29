# Declino Italia

Repository personale di analisi sul declino economico e sociale italiano. Le analisi usano solo API pubbliche: non sono previsti file Excel, CSV o dataset manuali come input. Le tabelle restano in memoria nei notebook e negli script; i grafici vengono mostrati nei notebook e, quando salvati come PNG di appoggio, restano file locali ignorati da Git.

Tutti i grafici riportano la fonte e la dicitura `elaborazione Nazareno Lecis`.

## Fonti

Fonti gia usate nei notebook e nelle funzioni:

- World Bank API: WDI, WGI e Doing Business storico.
- Eurostat API: produttivita reale, costo del lavoro per unita di prodotto, ore lavorate e serie da collegare per COFOG, prezzi e vendite.

Fonti con endpoint verificabile o da collegare per completare le categorie:

- ISTAT SDMX API: demografia territoriale, lavoro di dettaglio, CCNL, dualismo Nord-Sud.
- UN WPP Data Portal API: fasce demografiche non disponibili in WDI.
- OECD SDMX API: ore, produttivita, tassi, produzione, prezzi case, vendite al dettaglio, risparmio famiglie e R&S.
- Commissione europea - AMECO API: PIL potenziale, TFP, NAWRU, salari, spesa pubblica reale, investimenti e stock di capitale.
- MEF-RGS OpenBDAP API: bilancio pubblico italiano, entrate, spese e dataset amministrativi della Ragioneria Generale dello Stato.
- IMF API: debito, saldi fiscali, consolidamenti, WEO e serie storiche di finanza pubblica.
- ECB Data Portal API: tassi di riferimento, tassi di mercato, cambi.
- BIS SDMX API: cambi effettivi e prezzi delle abitazioni, dove piu adatto.
- Banca d'Italia API/portale dati: tassi, cambi e statistiche monetarie nazionali.
- ILOSTAT SDMX API: lavoro, disoccupazione, forze lavoro e salari.
- UN SDG API: indicatori internazionali di contesto.
- API elettorali ufficiali o equivalenti: partecipazione al voto e indicatori politici.

Il catalogo delle fonti sta in `sources/api_catalog.py`. Gli endpoint principali si verificano con:

```bash
python3 sources/check_sources.py
```

## Struttura

- `analisi/cruscotto/`: vista trasversale degli indicatori principali del progetto.
- `analisi/pil/`: PIL reale e nominale, PIL pro capite, produttivita, crescita media e crescita cumulata.
- `analisi/valore_aggiunto/`: valore aggiunto industriale e manifatturiero.
- `analisi/demografia/`: popolazione, fasce di eta, natalita, fertilita, dipendenze, migrazioni e aspettativa di vita.
- `analisi/occupazione/`: forze lavoro, occupazione, disoccupazione, ore lavorate e indicatori del mercato del lavoro.
- `analisi/salari/`: salari, compensazioni reali, quota salari, reddito disponibile e costo unitario del lavoro.
- `analisi/debito_pubblico/`: debito/PIL, saldi fiscali, entrate, spese e consolidamenti fiscali.
- `analisi/spesa_pubblica/`: spesa totale, consumi finali pubblici e capitoli di spesa.
- `analisi/investimenti/`: formazione di capitale, investimenti fissi, componenti reali e stock di capitale.
- `analisi/tassi_interesse/`: policy rate, tassi decennali e spread.
- `analisi/produzione/`: produzione industriale e produzione delle costruzioni.
- `analisi/settore_estero/`: import, export, saldo commerciale, partite correnti, NIIP e ragioni di scambio.
- `analisi/tasso_cambio/`: cambio bilaterale, cambio effettivo reale e cambio effettivo nominale.
- `analisi/dualismo_nord_sud/`: divari territoriali italiani su PIL e crescita.
- `analisi/prezzi/`: prezzi al consumo e prezzi delle abitazioni.
- `analisi/consumi_vendite/`: consumi privati, immatricolazioni, vendite al dettaglio e risparmio famiglie.
- `analisi/istruzione/`: capitale umano e iscrizione terziaria.
- `analisi/ricerca/`: R&S, brevetti, export high-tech e indicatori di innovazione.
- `analisi/istituzioni/`: burocrazia, governance, qualita regolatoria e indicatori istituzionali.
- `analisi/altri_grafici/`: computer per abitante, risparmi nazionali e turismo; voto e R&S restano nelle categorie tematiche dedicate.
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
- `analisi/salari/notebooks/01_grafici_salari.ipynb`
- `analisi/debito_pubblico/notebooks/01_grafici_debito_pubblico.ipynb`
- `analisi/spesa_pubblica/notebooks/01_grafici_spesa_pubblica.ipynb`
- `analisi/investimenti/notebooks/01_grafici_investimenti.ipynb`
- `analisi/tassi_interesse/notebooks/01_grafici_tassi_interesse.ipynb`
- `analisi/produzione/notebooks/01_grafici_produzione.ipynb`
- `analisi/settore_estero/notebooks/01_grafici_settore_estero.ipynb`
- `analisi/tasso_cambio/notebooks/01_grafici_tasso_cambio.ipynb`
- `analisi/dualismo_nord_sud/notebooks/01_grafici_dualismo_nord_sud.ipynb`
- `analisi/prezzi/notebooks/01_grafici_prezzi.ipynb`
- `analisi/consumi_vendite/notebooks/01_grafici_consumi_vendite.ipynb`
- `analisi/altri_grafici/notebooks/01_grafici_altri_indicatori.ipynb`
- `analisi/ricerca/notebooks/02_grafici_ricerca_api.ipynb`
- `analisi/istituzioni/notebooks/02_grafici_istituzioni_api.ipynb`

Nei notebook dei grafici sono definite le specifiche della singola categoria: titolo dell'analisi, tipo di grafico, fonte primaria, fonti alternative ufficiali, anno iniziale, ultimo dato richiesto, indicatori, trasformazioni e nome dell'output. Le funzioni generali stanno invece in `analisi/utils/grafici.py`: download API, trasformazioni ricorrenti, confronto con la distribuzione dei paesi avanzati e costruzione dei plot.

Le funzioni usate nei notebook sono nominate per dire cosa fanno:

- `definisci_grafico_da_indicatore_world_bank`: grafico generato da un singolo indicatore World Bank.
- `definisci_grafico_da_rapporto_world_bank`: grafico ottenuto combinando due indicatori World Bank.
- `registra_grafico_da_collegare_a_api`: grafico censito ma ancora da collegare alla fonte pubblica corretta.
- `genera_grafici_e_inventario`: scarica i dati, applica la trasformazione, genera il plot e restituisce l'inventario.

Ogni notebook mostra l'inventario della categoria e i plot generati dalle fonti gia mappate. I grafici non ancora collegati a una fonte restano tracciati come analisi da completare, senza introdurre input manuali.

## Variabili delle specifiche

Ogni grafico viene dichiarato nei notebook con una specifica leggibile. Le variabili principali e i valori ammessi o consigliati sono:

- `titolo`: testo libero; nome descrittivo dell'analisi mostrato anche nel plot.
- `nome_output`: testo tecnico in minuscolo con underscore; esempio `pil_reale_pro_capite_crescita_media`.
- `tipo_grafico`: metadato descrittivo. Valore usato oggi: `serie_storica`. Valori consigliati per estensioni: `mappa`, `barre`, `dispersione`, `tabella`.
- `fonte_primaria`: nome di una API censita in `sources/api_catalog.py`. Valori oggi previsti: `World Bank API`, `Eurostat API`, `AMECO API`, `AMECO SDMX`, `MEF-RGS OpenBDAP API`, `ISTAT SDMX API`, `OECD SDMX API`, `ECB Data Portal API`, `BIS SDMX API`, `Banca d'Italia API`, `ILOSTAT SDMX API`, `UN SDG API`, `IMF DataMapper API`, `UN WPP Data Portal API`.
- `fonti_alternative`: tupla di fonti API ufficiali, usando gli stessi nomi di `fonte_primaria`; esempio `('OECD SDMX API', 'Eurostat API')`.
- `anno_inizio`: intero; primo anno richiesto alla fonte API. Esempi: `1960`, `1970`, `1995`, `2000`.
- `ultimo_dato`: `latest` per usare l'ultimo dato disponibile; in alternativa un anno esplicito come testo o numero, per esempio `2023`.
- `indicatore`: codice dell'indicatore API quando il grafico usa una sola serie; esempio World Bank `NY.GDP.PCAP.KD`.
- `numeratore`: codice della serie al numeratore quando il grafico combina due serie.
- `denominatore`: codice della serie al denominatore quando il grafico combina due serie.
- `scala`: numero moltiplicativo applicato al risultato; valori tipici `1.0`, `100.0`, `0.01`.
- `operazione`: `ratio` per rapporto numeratore/denominatore, `product` per prodotto numeratore*denominatore*scala.
- `trasformazione`: trasformazione applicata prima del plot. Valori ammessi: `level` per livelli, `ratio` per serie gia calcolate come rapporto, `growth_10y` per crescita annualizzata su 10 anni, `index` per indice con anno base, `share_world` per quota italiana sul totale mondiale.
- `anno_base`: intero; anno base per `index`. Valore standard: `1970`.
- `finestra`: intero; numero di anni per `growth_10y`. Valore standard: `10`.
- `paesi`: tupla di codici ISO3. Default: paesi avanzati (`ITA`, `DEU`, `FRA`, `ESP`, `USA`, `JPN`, `GBR`, `CAN`, `AUS`, `AUT`, `BEL`, `CHE`, `DNK`, `FIN`, `NLD`, `NOR`, `SWE`, `PRT`, `GRC`, `IRL`). Per quote mondiali si usa anche `WLD`.
- `confronto`: booleano; `True` mostra Italia, min-max, percentile 25-75 e mediana dei paesi avanzati; `False` mostra solo le serie richieste.
- `cosa_mostra`: testo libero; spiegazione sintetica del contenuto del grafico.
- `note`: testo libero; dettaglio operativo, soprattutto per grafici ancora da collegare a una API.

`registra_grafico_da_collegare_a_api` usa le stesse variabili descrittive, ma marca il grafico come `in_attesa_mapping_api`: la fonte pubblica e censita, il codice di download specifico deve ancora essere scritto.

## Output

I grafici vengono visualizzati nei notebook. Quando una cella salva PNG di appoggio, i file vengono creati nella cartella della categoria ma non vengono versionati: `*.png` e' in `.gitignore`.

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
