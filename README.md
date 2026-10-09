# DSS per la Protezione Civile - Catania
*Tesi di Laurea Magistrale in Ingegneria Informatica*

Sistema di supporto alle decisioni (DSS) distribuito per la gestione e la valutazione d'impatto degli allarmi di protezione civile nel territorio comunale di Catania, basato sull'orchestrazione di workflow tramite **Dify** e sull'integrazione di dati geospaziali, demografici, meteorologici ed eventi in tempo reale.

---

## Architettura del Sistema
Il sistema adotta un approccio modulare e distribuito:
- **Motore di Workflow (Dify):** Gestisce la logica di business, l'orchestrazione delle fasi di analisi dell'allarme e la generazione automatica dei report di impatto per gli operatori.
- **Backend di Integrazione e Tool Python:** Una suite di moduli specializzati per l'interrogazione di API esterne (PredictHQ, Open-Meteo, Overpass/OpenStreetMap, Geoapify) e banche dati territoriali (ISTAT, idranti, Vigili del Fuoco).
- **API REST:** Comunicazione basata su chiamate HTTP POST per l'upload dei file di allarme (formato XML CAP) e l'esecuzione asincrona o bloccante dei workflow[cite: 5].

---

## Struttura della Repository e Moduli
La repository è organizzata nei seguenti componenti principali[cite: 5]:

```text
├── tesi_env/              # Ambiente virtuale Python (escluso da Git)
├── __pycache__/           # File di cache di Python (escluso da Git)
├── allarme.xml            # File di allarme iniziale in formato standard CAP
├── main.py                # Script principale di coordinamento ed esecuzione
├── cerca_eventi.py        # Integrazione API PredictHQ per eventi di massa e assembramenti
├── geoapify_tool.py       # Tool geospaziale e di geocodifica indirizzi
├── istat_tool.py          # Estrazione dati demografici ISTAT (densità e residenti)
├── open_meteo_tool.py     # Integrazione Open-Meteo per dati meteorologici in tempo reale
├── overpass_api.py        # Interrogazione Overpass/OSM per punti sensibili e scuole
├── elenco_idranti.py      # Gestione e mappatura delle risorse idriche e idranti
├── vvf.py                 # Modulo per il calcolo della stima d'intervento dei Vigili del Fuoco
├── servizi_territorio.py  # Analisi di supporto dei servizi territoriali[cite: 5]
├── simulazione.py         # Script per la simulazione e il test degli scenari[cite: 5]
├── .env                   # Variabili d'ambiente e token segreti (escluso da Git)[cite: 5]
├── .env.example           # Modello di configurazione per le variabili d'ambiente[cite: 5]
├── .gitignore             # File di configurazione per l'esclusione di file sensibili[cite: 5]
└── README.md              # Documentazione del progetto
