# GeoCetus API v2

La **GeoCetus API v2** è un'interfaccia REST progettata per fornire accesso standardizzato ai dati degli spiaggiamenti di cetacei e tartarughe marine lungo le coste italiane.  
Include un sistema avanzato di filtraggio basato su parametri geografici, temporali e biologici.

🔗 **Documentazione Swagger:** https://www.geocetus.it/gcapi/docs

---

## 🧰 Tecnologie principali

- **Python 3.10+**
- **FastAPI**
- **Uvicorn**
- **PostgreSQL + PostGIS** (opzionale)
- **Pydantic**
- **Requests / AioHTTP**
- Struttura modulare progettata per estendibilità e scalabilità

---

## 📦 Installazione

Clona la repository:

```bash
git clone https://github.com/<user>/GCApi.git
cd GCApi
```

Crea e attiva un ambiente virtuale:

```bash
python3 -m venv gc_api_env
source gc_api_env/bin/activate
```

Installa i requisiti:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configurazione

Il file `config.json` **non è incluso nella repository** perché contiene dati sensibili ed è incluso nel `.gitignore`.

Crea il file a partire da un template:

```bash
cp config.example.json config.json
```

Esempio struttura:

```json
{
  "db_host": "localhost",
  "db_port": 5432,
  "db_user": "utente",
  "db_password": "password",
  "db_name": "geocetus",
  "api_key": "INSERISCI_CHIAVE"
}
```

---

## 🚀 Avvio dell’API

Avvio in modalità sviluppo:

```bash
uvicorn api:app --reload
```

L'API sarà disponibile su:

```
http://localhost:8000
```

Swagger UI:  
```
http://localhost:8000/docs
```

ReDoc:  
```
http://localhost:8000/redoc
```

---

## 🔍 Endpoints principali

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/records` | Recupera record filtrati |
| GET | `/stats` | Statistiche aggregate |
| GET | `/health` | Verifica stato dell'API |
| GET | `/species` | Elenco delle specie presenti nel dataset |
| GET | `/regions` | Elenco delle regioni disponibili |

---

## 🗂 Struttura del progetto

```
GCApi/
│── api.py                # entrypoint FastAPI
│── config.json           # configurazione sensibile (ignored)
│── config.example.json   # template configurazione
│── requirements.txt
│── README.md
│── gc_api_env/           # ambiente virtuale (ignored)
│── routers/              # router modulari (opzionale)
│── models/               # modelli Pydantic
│── services/             # funzioni logiche e servizi
│── utils/                # funzioni di utilità
```

---

## 🔐 Sicurezza

- `config.json` è ignorato tramite `.gitignore`
- Nessuna credenziale sensibile deve essere committata
- Possibilità di usare variabili d'ambiente in produzione (`os.getenv()`)

---

## 🧪 Testing

Esegui i test con:

```bash
pytest
```

---

## 🤝 Contributi

I contributi sono benvenuti!  
Apri una *Issue* o invia una *Pull Request*.

---

## 📄 Licenza

Progetto rilasciato sotto licenza **MIT** (modificabile secondo necessità).

---

## 🐬 About

GeoCetus è un progetto dedicato alla raccolta, standardizzazione e diffusione libera dei dati sugli spiaggiamenti di cetacei e tartarughe in Italia, nell’ottica dell’Open Data e della ricerca scientifica.
