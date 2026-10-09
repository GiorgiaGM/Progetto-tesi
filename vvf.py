import os
import math
import requests
from dotenv import load_dotenv

load_dotenv("tesi_env/.env")
geoapify_key = os.getenv("GEOAPIFY_API_KEY")


def haversine(lat1, lon1, lat2, lon2):
    """
    Calcola la distanza in metri tra due punti geografici usando la formula di Haversine.
    """
    R = 6371000  # Raggio della Terra in metri
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def get_distaccamenti_live(lat, lng):
    """
    Interrogo Geoapify per trovare i VVF nel raggio di 10km.
    """
    url = f"https://api.geoapify.com/v2/places"
    
    params = {
        "categories": "service.fire_station",
        "filter": f"circle:{lng},{lat},10000",
        "bias": f"proximity:{lng},{lat}",
        "limit": 5,
        "apiKey": geoapify_key
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    distaccamenti = []
    
    for feature in data.get('features', []):
        props = feature['properties']
        distaccamenti.append({
            "nome": props.get('name', 'Distaccamento VVF Generico'),
            "lat": feature['geometry']['coordinates'][1],
            "lng": feature['geometry']['coordinates'][0]
        })
    return distaccamenti



def calcola_distanza_e_eta(lat_incendio: float, lng_incendio: float) -> dict:
    """
    Recupera i distaccamenti e calcola il più vicino con relativa ETA.
    """
    distaccamenti = get_distaccamenti_live(lat_incendio, lng_incendio)
    
    # Controllo di sicurezza se la lista è vuota o le coordinate sono 0.0
    if not distaccamenti:
        return {
            "vvf_competente": "Nessun distaccamento VVF trovato nelle vicinanze",
            "distanza_metri": 0,
            "tempo_arrivo_stimato_minuti": 0
        }
    
    distaccamento_piu_vicino = None
    distanza_minima = float('inf')
    
    for d in distaccamenti:
        # Utilizzo della funzione Haversine
        distanza_metri = haversine(lat_incendio, lng_incendio, d["lat"], d["lng"])
        
        if distanza_metri < distanza_minima:
            distanza_minima = distanza_metri
            distaccamento_piu_vicino = d
            
    velocita_mezzi = 11.1  # circa 40 km/h
    tempo_secondi = distanza_minima / velocita_mezzi
    tempo_minuti = round((tempo_secondi / 60) + 2)
    
    return {
        "vvf_competente": distaccamento_piu_vicino["nome"],
        "distanza_metri": round(distanza_minima),
        "tempo_arrivo_stimato_minuti": tempo_minuti
    }

if __name__ == "__main__":
    # Test con coordinate di Catania (es. Via Etnea)
    lat_test, lng_test = 37.5074, 15.0873
    
    print("=" * 50)
    print(f"TEST VVF (Ricerca attorno a lat: {lat_test}, lng: {lng_test})")
    print("=" * 50)
    
    risultato = calcola_distanza_e_eta(lat_test, lng_test)
    
    import json
    print(json.dumps(risultato, indent=4, ensure_ascii=False))
