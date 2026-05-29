from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FonteApi:
    nome: str
    ente: str
    url_controllo: str
    aree: tuple[str, ...]
    note: str
    accept: str = "application/json, application/xml, text/html, */*"
    timeout: int = 20
    obbligatoria: bool = True


FONTI_API: tuple[FonteApi, ...] = (
    FonteApi(
        nome="World Bank API",
        ente="World Bank",
        url_controllo="https://api.worldbank.org/v2/country/ITA/indicator/NY.GDP.MKTP.KD?format=json&per_page=5",
        aree=("PIL", "demografia", "finanza pubblica", "settore estero", "prezzi", "turismo"),
        note="WDI, WGI e indicatori storici Doing Business.",
    ),
    FonteApi(
        nome="Eurostat API",
        ente="European Commission - Eurostat",
        url_controllo=(
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_lp_ulc"
            "?format=JSON&lang=en&freq=A&unit=I15&na_item=RLPR_HW&geo=IT&time=2023"
        ),
        aree=("produttivita", "lavoro", "COFOG", "prezzi", "vendite", "regioni"),
        note="Statistiche europee via dissemination API.",
    ),
    FonteApi(
        nome="AMECO API",
        ente="Commissione europea - DG ECFIN",
        url_controllo=(
            "https://webgate.ec.europa.eu/ecfin/redisstat/api/dissemination/statistics/1.0/data/"
            "ameco_chapter01-03?format=JSON&lang=en"
        ),
        aree=("PIL potenziale", "TFP", "NAWRU", "salari", "spesa pubblica", "investimenti", "stock di capitale"),
        note="Database AMECO esposto dal servizio redisstat della Commissione europea.",
    ),
    FonteApi(
        nome="AMECO SDMX",
        ente="Commissione europea - DG ECFIN",
        url_controllo="https://webgate.ec.europa.eu/ecfin/redisstat/api/dissemination/sdmx/2.1/dataflow/ECFIN/all/latest",
        aree=("catalogo AMECO", "metadati"),
        note="Endpoint SDMX per scoprire dataflow e strutture AMECO.",
        accept="application/vnd.sdmx.structure+xml, application/xml, */*",
    ),
    FonteApi(
        nome="MEF-RGS OpenBDAP API",
        ente="Ministero dell'Economia e delle Finanze - Ragioneria Generale dello Stato",
        url_controllo="https://bdap-opendata.rgs.mef.gov.it/SpodCkanApi/api/3/action/package_list",
        aree=("bilancio pubblico", "finanza pubblica italiana", "spesa pubblica", "entrate"),
        note="Catalogo CKAN OpenBDAP della RGS/MEF.",
    ),
    FonteApi(
        nome="ISTAT SDMX API",
        ente="ISTAT",
        url_controllo="https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/all/latest",
        aree=("demografia", "lavoro", "territori", "prezzi", "CCNL", "Nord-Sud"),
        note="Endpoint SDMX ufficiale ISTAT.",
    ),
    FonteApi(
        nome="OECD SDMX API",
        ente="OECD",
        url_controllo="https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest",
        aree=("produttivita", "ore lavorate", "tassi", "produzione", "prezzi case", "R&S"),
        note="Cataloghi e dataset OECD in SDMX.",
        timeout=60,
    ),
    FonteApi(
        nome="ECB Data Portal API",
        ente="European Central Bank",
        url_controllo="https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1",
        aree=("tassi", "cambi", "mercati finanziari"),
        note="Endpoint SDMX del Data Portal ECB.",
        accept="application/vnd.sdmx.genericdata+xml, application/xml, */*",
    ),
    FonteApi(
        nome="BIS SDMX API",
        ente="Bank for International Settlements",
        url_controllo="https://stats.bis.org/api/v1/dataflow",
        aree=("cambi effettivi", "prezzi abitazioni", "credito", "mercati finanziari"),
        note="Catalogo dataflow BIS in SDMX.",
        accept="application/xml, application/json, */*",
    ),
    FonteApi(
        nome="Banca d'Italia API",
        ente="Banca d'Italia",
        url_controllo="https://www.bancaditalia.it/statistiche/basi-dati/bds/index.html",
        aree=("tassi", "cambi", "statistiche monetarie", "finanza"),
        note="Portale dati statistici Banca d'Italia; endpoint applicativi da mappare sulle singole serie.",
        obbligatoria=False,
    ),
    FonteApi(
        nome="ILOSTAT SDMX API",
        ente="International Labour Organization",
        url_controllo="https://sdmx.ilo.org/rest/dataflow/ILO/all/latest",
        aree=("occupazione", "disoccupazione", "forze lavoro", "salari"),
        note="Catalogo ILOSTAT in SDMX.",
    ),
    FonteApi(
        nome="UN SDG API",
        ente="United Nations Statistics Division",
        url_controllo="https://unstats.un.org/sdgapi/v1/sdg/Goal/List",
        aree=("indicatori internazionali", "sviluppo", "contesto"),
        note="API ufficiale UNSD; utile come fonte alternativa per indicatori globali.",
    ),
    FonteApi(
        nome="IMF DataMapper API",
        ente="International Monetary Fund",
        url_controllo="https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/ITA",
        aree=("WEO", "PIL", "debito", "saldi fiscali", "partite correnti"),
        note="API IMF DataMapper; in alcuni ambienti puo rispondere con blocco anti-bot pur restando fonte da mappare.",
        obbligatoria=False,
    ),
    FonteApi(
        nome="UN WPP Data Portal API",
        ente="United Nations Population Division",
        url_controllo="https://population.un.org/dataportalapi/api/v1/data/indicators/49/locations/380/start/2023/end/2023",
        aree=("demografia", "fasce di eta", "fecondita", "aspettativa di vita"),
        note="API del Data Portal UN Population; puo richiedere chiave o autorizzazione.",
        obbligatoria=False,
    ),
)
