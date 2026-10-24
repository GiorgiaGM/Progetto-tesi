import os
import uuid
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import requests
from database import init_db, salva_report_html, ottieni_report_html
from overpass_api import determina_tipo_area_e_raggio_overpass
from open_meteo_tool import get_weather_context
from istat_tool import get_demographic_context
from geoapify_tool import cerca_strutture_critiche, geoapify_key 
from vvf import calcola_distanza_e_eta
from elenco_idranti import trova_idranti_vicini
from cerca_eventi import cerca_eventi

load_dotenv("tesi_env/.env")

app = FastAPI(
    title="API Protezione Civile - Catania",
    description="Endpoint geospaziali e ambientali per l'integrazione nel Decision Support System con Dify",
    version="1.0.0"
)

# Inizializzo la tabella MySQL all'avvio dell'applicazione
init_db()

# Configurazione Dify
DIFY_API_URL = os.getenv("DIFY_API_URL")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")


@app.post("/salva-report-dify")
async def salva_report_da_dify(request: Request):
    """
    Endpoint chiamato dal nodo HTTP Request di Dify.
    Riceve l'HTML, usa la funzione salva_report_html di database.py
    e restituisce il link con l'ID.
    """
    try:
        body_bytes = await request.body()
        html_content = body_bytes.decode("utf-8")
        
        if not html_content:
            raise HTTPException(status_code=400, detail="Contenuto HTML mancante")
        
        # Isolo l'HTML a partire da <!DOCTYPE html>
        html_content = html_content.strip()
        
        # Rimozione di eventuali graffe residue se presenti all'inizio o alla fine
        while html_content.startswith("{"):
            html_content = html_content[1:].strip()
        while html_content.endswith("}"):
            html_content = html_content[:-1].strip()
            
        doctype_index = html_content.find("<!DOCTYPE html>")
        if doctype_index != -1:
            html_content = html_content[doctype_index:]
            
        report_id = str(uuid.uuid4())[:8]
        
        salva_report_html(report_id, html_content)
        
        url_report = f"http://localhost:8000/report/{report_id}"
        print(f"[SUCCESS] Report salvato con ID: {report_id}")
        
        return PlainTextResponse(url_report)
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/{report_id}", response_class=HTMLResponse)
def visualizza_report(report_id: str):
    """
    Web Server: serve la pagina HTML con la mappa Leaflet a chi clicca sul link.
    """
    html_content = ottieni_report_html(report_id)
    if not html_content:
        raise HTTPException(status_code=404, detail="Report non trovato nel database.")
    
    return HTMLResponse(content=html_content, status_code=200)


class SegnalazioneCollega(BaseModel):
    segnalazione: str
    query: str = "Analizza questa segnalazione"

@app.post("/ricevi-da-collega")
def ricevi_e_interroga_dify(dati: SegnalazioneCollega):
    """
    Ricevo la segnalazione dal sistema del collega, la invio a Dify
    e restituisco il report finale di protezione civile.
    """
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {
            "segnalazione": dati.segnalazione
        },
        "query": dati.query,
        "response_mode": "blocking",
        "user": "sistema-collega"
    }
    
    try:
        # Inoltra la richiesta a Dify
        response = requests.post(DIFY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        dify_response = response.json()
        
        print("RISPOSTA GREZZA DIFY:", dify_response)  # stampa il report sul terminale
        
        # Estrae l'answer generata da Dify
        report_finale = dify_response.get("data", {}).get("outputs", {}).get("text", "Nessuna risposta generata")
        
        return {
            "status": "success",
            "report_emergenza": report_finale
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore di comunicazione con Dify: {str(e)}")



@app.get("/analisi-emergenza")
def analizza_area(lat: float = Query(..., examples=37.5234), lng: float = Query(..., examples=15.0931), orario: str = Query("08:00", description="Orario simulato HH:MM per il test")):
    """
    Raccoglie in un unico payload tutti i dati geospaziali ed ambientali. 
    """
    # Calcolo Vulnerabilità Scolastica ed orario
    try:
        hour = int(orario.split(":")[0])
    except Exception:
        hour = 8

    if hour == 8:
        vulnerabilita_scuole = "ALTA"
        motivazione_orario = "Orario di punta per l'ingresso degli studenti nelle scuole (elevato afflusso di pedoni e traffico mattutino)."
    elif hour == 13:
        vulnerabilita_scuole = "ALTA"
        motivazione_orario = "Orario di punta per l'uscita degli studenti dalle scuole (elevata concentrazione di persone e traffico nell'area)."
    elif 9 <= hour <= 18:
        vulnerabilita_scuole = "MEDIA"
        motivazione_orario = "Orario di svolgimento attività scolastiche/pomeridiane."
    else:
        vulnerabilita_scuole = "BASSA"
        motivazione_orario = "Orario serale/notturno (strutture scolastiche chiuse, basso afflusso)."
    
    # Calcolo del raggio e del tipo di area
    tipo_area, raggio = determina_tipo_area_e_raggio_overpass(lat, lng)
    print(f"[MAIN] Raggio calcolato: {raggio}m (Area: {tipo_area.upper()})")
    
    # Ricerca Eventi/Manifestazioni con PredictHQ
    try:
        eventi_raw = cerca_eventi(lat=lat, lng=lng, orario=orario, raggio_metri=raggio)
        if eventi_raw:
            lista_eventi = [
                f"[{ev['categoria'].upper()}] {ev['titolo']} (dalle {ev['inizio']} alle {ev['fine']})"
                for ev in eventi_raw
            ]
            info_evento = "; ".join(lista_eventi)
        else:
            info_evento = f"Nessun evento pubblico o manifestazione rilevata nel raggio di {raggio}m all'orario indicato ({orario})."
    except Exception as e:
        info_evento = f"Errore durante il recupero eventi: {str(e)}"
        
    
    # Recupera dati meteo
    meteo_data = get_weather_context(lat, lng)
    
    # Recupera dati demografici ISTAT
    istat_data = get_demographic_context(lat, lng, raggio_metri=raggio,tipo_area=tipo_area)
    
    # Recupera strutture critiche Geoapify
    try:
        geoapify_raw = cerca_strutture_critiche(lat, lng, geoapify_key, raggio_metri=raggio)
        features = geoapify_raw.get("features", [])
        strutture = []
        for f in features[:5]: # Limito alle prime 5 strutture rilevanti per non rallentare l'LLM
            p = f.get("properties", {})
            strutture.append({
                "nome": p.get("name", "Struttura generica"),
                "categorie": p.get("categories", []),
                "distanza_metri": p.get("distance", "N/D")
            })
    except Exception as e:
        strutture = f"Errore Geoapify: {str(e)}"

    # Calcola la logistica di soccorso dei Vigili del Fuoco
    vvf_data = calcola_distanza_e_eta(lat, lng)
    
    # Recupera gli idranti vicini accessibili (Buona o Ottima)
    try:
        idranti_data = trova_idranti_vicini(lat, lng)
    except Exception as e:
        idranti_data = f"Errore ricerca idranti: {str(e)}"
    
    # Unifica tutto nel payload finale richiesto da Dify
    return {
        "coordinate_evento": {"latitudine": lat, "longitudine": lng},
        "orario_contestuale": {
            "ora": orario,
            "vulnerabilita_scuole": vulnerabilita_scuole,
            "motivazione_orario": motivazione_orario,
            "eventi_trovati": info_evento
        },
        "livello_meteo": meteo_data,
        "livello_demografico_istat": istat_data,
        "strutture_critiche_vicine": strutture,
        "soccorso_vvf": {
            "vvf_competente": vvf_data["vvf_competente"],
            "distanza_metri": vvf_data["distanza_metri"],
            "tempo_arrivo_stimato_minuti": vvf_data["tempo_arrivo_stimato_minuti"]
        },
        "idranti_disponibili": idranti_data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)