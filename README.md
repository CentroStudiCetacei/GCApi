
## 📝 Introduzione

La **GeoCetus API v2** è un’interfaccia REST progettata per fornire accesso standardizzato ai dati degli **spiaggiamenti di cetacei e tartarughe marine** lungo le coste italiane.  
Include un sistema avanzato di filtraggio basato su parametri **geografici, temporali e biologici**.

### 🔍 Novità Principale  
Gestione intelligente del parametro **species**, che accetta sia **nomi scientifici** che **nomi comuni**, normalizzando automaticamente l’input al nome scientifico corretto.

---

## 🏛 Architettura Generale

Stack tecnologico adottato:

- **FastAPI** – framework REST moderno e performante  
- **Uvicorn** – ASGI server ad alte prestazioni  
- **Apache2** – reverse proxy pubblico  
- **PostgreSQL / PostGIS** – database spaziale  
- **Viste principali:** `v_cetacei`, `v_tartarughe`  
- **Tabelle lookup:** `specie_cetacei`, `specie_tartarughe`, `regioni`

📌 **Base URL:**  
https://www.geocetus.it/gcapi/v2/

---

## 🔗 Endpoint Principali

| Metodo | Endpoint | Descrizione | Esempio |
|--------|----------|-------------|---------|
| GET | `/v2/records` | Restituisce una FeatureCollection GeoJSON filtrabile | https://www.geocetus.it/gcapi/v2/records?table=T&limit=5 |
| GET | `/v2/species` | Elenco delle specie disponibili | https://www.geocetus.it/gcapi/v2/species?table=C |
| GET | `/v2/regions` | Elenco delle regioni italiane disponibili | https://www.geocetus.it/gcapi/v2/regions |
| GET | `/gcapi/docs` | Swagger UI interattiva | https://www.geocetus.it/gcapi/docs |
| GET | `/gcapi/openapi.json` | Schema OpenAPI completo | https://www.geocetus.it/gcapi/openapi.json |

---

## 📌 Parametri Supportati (sintesi)

I principali parametri accettati dagli endpoint di filtraggio includono:

- `species` — nome comune o scientifico (normalizzato automaticamente)  
- `region` — filtra per regione  
- `date_from` / `date_to` — filtri temporali  
- `limit` — numero massimo di record  
- `table` — specifica la tabella: `T` (tartarughe) oppure `C` (cetacei)

---

## 📦 Output

Tutti i risultati dei record vengono restituiti in formato **GeoJSON**, compatibile con:

- QGIS  
- ArcGIS  
- WebGIS (Leaflet, Mapbox, OpenLayers)  
- Python (GeoPandas, Shapely)  


## 🐬 About

GeoCetus è un progetto dedicato alla raccolta, standardizzazione e diffusione libera dei dati sugli spiaggiamenti di cetacei e tartarughe in Italia, nell’ottica dell’Open Data e della ricerca scientifica.

**Ti chiediamo di citare questo lavoro in caso di utilizzo dei dati GeoCetus / Please cite this work when using GeoCetus data:**

> Di Lorenzo, A.; Di Renzo, L.; Profico, C.; Profico, D.; Olivieri, V.; Guccione, S. *GeoCetus: A Multi-Decadal Open Geospatial Infrastructure for the Continuous Monitoring of Marine Strandings in Italy*. **Animals** 2026, 16, 1323. https://doi.org/10.3390/ani16091323
