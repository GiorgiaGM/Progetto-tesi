import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv("tesi_env/.env")

PREDICTHQ_TOKEN = os.getenv("PREDICTHQ_TOKEN")

def cerca_eventi(
    lat: float = 37.5234, 
    lng: float = 15.0931, 
    orario: str = "08:00", 
    raggio_metri: float = 500.0,
    durata_stimata_ore: int = 3
) -> list:
    """
    Trova gli eventi in zona convertendo gli orari da UTC a orario locale italiano (Europe/Rome).
    """
    if not PREDICTHQ_TOKEN:
        print("Attenzione: PREDICTHQ_TOKEN non trovato nel file .env")
        return []

    url = "https://api.predicthq.com/v1/events/"
    headers = {
        "Authorization": f"Bearer {PREDICTHQ_TOKEN}",
        "Accept": "application/json"
    }

    # Fuso orario locale italiano
    tz_locale = ZoneInfo("Europe/Rome")
    
    # Data odierna locale
    oggi_locale = datetime.now(tz_locale).date()

    params = {
        "within": f"{int(raggio_metri)}m@{lat},{lng}",
        "active.gte": f"{oggi_locale}T00:00:00Z",
        "active.lte": f"{oggi_locale}T23:59:59Z",
        "limit": 10,
        "sort": "-rank",
        "category": "sports,concerts,festivals,performing-arts,expos,conferences"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        
        # Creo l'oggetto datetime dell'emergenza con il fuso orario locale
        ora_int, min_int = map(int, orario.split(":"))
        dt_emergenza = datetime.combine(oggi_locale, datetime.min.time()).replace(
            hour=ora_int, minute=min_int, tzinfo=tz_locale
        )

        eventi_rilevanti = []
        for event in results:
            start_raw = event.get("start")
            end_raw = event.get("end")

            if not start_raw:
                continue

            # Parsing dell'orario UTC dall'API
            start_clean = start_raw.replace("Z", "").split(".")[0]
            dt_inizio_utc = datetime.strptime(start_clean, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=ZoneInfo("UTC"))
            
            # Conversione dell'orario in ora locale italiana (UTC+2 in ora legale / UTC+1 in ora solare)
            dt_inizio_loc = dt_inizio_utc.astimezone(tz_locale)

            # Gestione ora di fine (se assente o uguale all'inizio, aggiunge durata_stimata_ore)
            if not end_raw or end_raw == start_raw:
                dt_fine_loc = dt_inizio_loc + timedelta(hours=durata_stimata_ore)
            else:
                end_clean = end_raw.replace("Z", "").split(".")[0]
                dt_fine_utc = datetime.strptime(end_clean, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=ZoneInfo("UTC"))
                dt_fine_loc = dt_fine_utc.astimezone(tz_locale)
                if dt_fine_loc == dt_inizio_loc:
                    dt_fine_loc = dt_inizio_loc + timedelta(hours=durata_stimata_ore)

            # Sottrae 1 ora per l'afflusso e azzera i minuti per coprire l'ora piena (es. 20:30 -> 19:30 -> 19:00)
            dt_inizio_afflusso = (dt_inizio_loc - timedelta(hours=1)).replace(minute=0, second=0)

            # Controllo se l'emergenza rientra nell'intervallo dell'evento
            if dt_inizio_afflusso <= dt_emergenza <= dt_fine_loc:
                eventi_rilevanti.append({
                    "titolo": event.get("title", "Evento generico"),
                    "categoria": event.get("category", "N/D"),
                    "inizio": dt_inizio_loc.strftime("%H:%M"),
                    "fine": dt_fine_loc.strftime("%H:%M"),
                    "etichette": event.get("labels", []),
                    "coordinate": event.get("location")
                })

        print(f"[DEBUG PredictHQ] Eventi attivi alle {orario} (ora locale): {len(eventi_rilevanti)}")
        return eventi_rilevanti

    except Exception as e:
        print(f"Errore durante la chiamata a PredictHQ: {e}")
        return []