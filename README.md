# DSS per la Protezione Civile - Catania
*Tesi di Laurea Magistrale in Ingegneria Informatica*

Sistema di supporto alle decisioni (DSS) distribuito per la gestione e la valutazione d'impatto degli allarmi di protezione civile nel territorio comunale di Catania, basato sull'orchestrazione di workflow tramite **Dify** e sull'integrazione di dati geospaziali, demografici, meteorologici ed eventi in tempo reale.

---

## Architettura del Sistema
Il sistema adotta un approccio modulare e distribuito:
- **Motore di Workflow (Dify):** Gestisce la logica di business, l'orchestrazione delle fasi di analisi dell'allarme e la generazione automatica dei report di impatto per gli operatori.
- **Backend di Integrazione e Tool Python:** Fornisce le API REST per la ricezione e la persistenza dei report (tramite richieste HTTP POST da Dify) e per la visualizzazione delle pagine HTML interattive complete di mappa Leaflet (tramite richieste HTTP GET dal browser). Include inoltre una suite di moduli specializzati per l'interrogazione di API esterne (PredictHQ, Open-Meteo, Overpass API, Geoapify) e banche dati territoriali (ISTAT, elenco di idranti).
- **API REST:** Comunicazione basata su chiamate HTTP POST per l'upload dei file di allarme (formato XML CAP) e l'esecuzione del workflow.

---

## Struttura della Repository e Moduli
La repository è organizzata nei seguenti componenti principali:

```text
├── tesi_env/              # Ambiente virtuale Python (escluso da Git)
├── __pycache__/           # File di cache di Python (escluso da Git)
├── File_allarme.xml       # File di allarme iniziale in formato standard CAP
├── main.py                # Script principale di coordinamento ed esecuzione
├── database.py            # Modulo di connessione al database e salvataggio/recupero dei report
├── cerca_eventi.py        # Integrazione API PredictHQ per eventi di massa e assembramenti
├── geoapify_tool.py       # Tool geospaziale e di geocodifica indirizzi
├── istat_tool.py          # Estrazione dati demografici ISTAT (densità e residenti)
├── open_meteo_tool.py     # Integrazione Open-Meteo per dati meteorologici in tempo reale
├── overpass_api.py        # Interrogazione Overpass/OSM per punti sensibili e scuole
├── elenco_idranti.py      # Gestione e mappatura delle risorse idriche e idranti
├── vvf.py                 # Modulo per il calcolo della stima d'intervento dei Vigili del Fuoco
├── servizi_territorio.py  # Analisi di supporto dei servizi territoriali
├── simulazione.py         # Script per la simulazione e il test degli scenari
├── .env                   # Variabili d'ambiente e token segreti (escluso da Git)
├── .env.example           # Modello di configurazione per le variabili d'ambiente
├── .gitignore             # File di configurazione per l'esclusione di file sensibili
└── README.md              # Documentazione del progetto

## Guida all'Avvio e Installazione 
1. Installare i pacchetti necessari per il progetto: 
pip install fastapi uvicorn requests python-dotenv mysql-connector-python pandas shapely

2. Copiare il file di esempio .env.example rinominandolo in .env e inserire le chiavi API e i parametri di connessione al database MySQL:
cp .env.example .env

3. Avvio del Database (MySQL)
Aprire il **XAMPP Control Panel** e cliccare su **Start** in corrispondenza del modulo **MySQL**.
Aprire **MySQL Workbench** e connettiti all'istanza locale (`localhost`, utente `root`).
Esegui i seguenti comandi SQL per creare e selezionare il database del progetto:
  CREATE DATABASE protezione_civile_db;
  USE protezione_civile_db;

4. Avviare il backend FastAPI tramite il server Uvicorn:
python main.py

5. Avviare l'applicazione Ollama sul tuo sistema per consentire l'esecuzione del modello linguistico locale.

6. Avviare Docker Desktop come *Amministratore*. Dalla dashboard di Docker, puoi cliccare direttamente sul link della porta **`80:80`** (o sulla porta configurata) del container Nginx per accedere rapidamente all'interfaccia web di Dify.

## Test e Validazione del Sistema

È possibile testare e convalidare l'intero flusso del Decision Support System attraverso due modalità:

### Opzione A: Interfaccia Grafica (Dify)
1. Accedi alla dashboard web di **Dify** (tramite Docker).
2. Apri il **Workflow di Protezione Civile** e clicca su **Esegui Test**.
3. Carica il file d'allarme XML nel blocco **Inizio** e avvia l'elaborazione.
4. Verifica la generazione del report e accedi al link HTTP restituito dal server FastAPI.

### Opzione B: Test tramite Postman

Step 1: Caricamento del File d'Allarme
Invia una richiesta `POST` in formato `form-data` all'endpoint di Dify per caricare il documento XML:
* **URL:** `http://localhost/v1/files/upload`
* **Headers:** 
  * `Authorization: Bearer app-EBJklQtKFbAXOWLBPK0OO4TO`
* **Body (`form-data`):**
  * `file`: Seleziona il file XML di test (es. `file_allarme2.xml`)
  * `user`: `operatore`

**Nota Importante:** Dalla risposta JSON di questa richiesta, copia il valore del campo **`id`** generato dal sistema (es. `"b6bdd658-1545-4ec5-8ec6-78b6f96609d7"`).

Step 2: Esecuzione del Workflow
Incolla l'`id` appena copiato all'interno del payload JSON e invia la richiesta `POST` per avviare l'elaborazione:
* **URL:** `http://localhost/v1/workflows/run`
* **Headers:** 
  * `Authorization: Bearer app-EBJklQtKFbAXOWLBPK0OO4TO`
  * `Content-Type: application/json`
* **Body (`raw` JSON):**
```json
{
  "inputs": {
    "time": "13:00",
    "File_allarme": {
      "type": "document",
      "transfer_method": "local_file",
      "upload_file_id": "INSERISCI_QUI_L_ID_RICEVUTO_DAL_PRIMO_STEP"
    }
  },
  "response_mode": "blocking",
  "user": "operatore"
}

> **Risultato finale:** Il workflow elaborerà i dati, interrogherà il server FastAPI (`main.py`) per i servizi geospaziali e la persistenza su MySQL, restituendo con successo il JSON con il link interattivo del report:
> ```json
> {
>   "outputs": {
>     "link_report": "http://localhost:8000/report/80c7d2a3"
>   }
> }
> ```
