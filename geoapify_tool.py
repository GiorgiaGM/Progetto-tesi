import os
import requests
from dotenv import load_dotenv

load_dotenv("tesi_env/.env")
geoapify_key = os.getenv("GEOAPIFY_API_KEY")

def cerca_strutture_critiche(lat, lng, geoapify_key, raggio_metri=float, categorie=None):
    """
    Interrogo l'API Places di Geoapify per capire se in quella zona ci sono strutture vulnerabili
    """
    
    if categorie is None:
       categorie = [
            # STRUTTURE VULNERABILI
            "education.school", 
            "education.university",
            "healthcare.hospital",
            "healthcare.clinic_or_praxis",
            "service.social_facility",           # Case di cura / Strutture di assistenza

            # CORPI DI SOCCORSO E EMERGENZA
            "service.fire_station", 
            "service.police",
            "emergency.disaster_response",       # Centri gestione disastri / Soccorso
            "emergency.disaster_help_point",     # Centri gestione disastri / Punti di aiuto

            # TRASPORTI E VIE DI FUGA
            "public_transport.train",      # Stazioni ferroviarie
            "public_transport.subway",     # Stazioni metropolitane
            "public_transport.subway.entrance", # Ingressi della metropolitana
            "airport",                     # Aeroporto generico
            "airport.terminal",            # Terminal aeroportuali
            "airport.international",       # Aeroporti internazionali

            # RETI E INFRASTRUTTURE CRITICHE
            "power.plant",                       # Centrali elettriche
            "power.substation",                  # Cabine elettriche di trasformazione
            "power.line",                        # Linee elettriche
            "office.telecommunication",          # Nodi e uffici TLC / ripetitori
            "office.water_utility",              # Infrastrutture idriche

            # RISCHIO INDUSTRIALE
            "production.factory",                # Fabbriche e stabilimenti della zona industriale
            "commercial.gas",                    # Depositi di gas/combustibile
            "service.vehicle.fuel"               # Stazioni di servizio / Distributori
        ]

    url = "https://api.geoapify.com/v2/places"
    
    params = {
        "categories": ",".join(categorie),
        "filter": f"circle:{lng},{lat},{raggio_metri}",
        "bias": f"proximity:{lng},{lat}",
        "limit": 30,
        "apiKey": geoapify_key
    }
    
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    lat, lng = 37.44954834129635, 15.08518378674863

    print("=" * 50)
    print(f"TEST GEOAPIFY PLACES (Raggio attorno a {lat}, {lng})")
    print("=" * 50)
    
    try:
        risposta = cerca_strutture_critiche(lat, lng, geoapify_key)
        
        features = risposta.get("features", [])
        print(f"Trovati {len(features)} Punti di Interesse rilevanti.\n")
        
        for f in features:
            proprieta = f.get("properties", {})
            nome = proprieta.get("name", "Nome non disponibile (Struttura generica)")
            cat_rilevate = proprieta.get("categories", [])
            distanza = proprieta.get("distance", "N/D")
            
            print(f" LUOGO: {nome}")
            print(f"   | Categorie: {cat_rilevate}")
            print(f"   | Distanza: {distanza} metri dal sensore")
            print("-" * 40)
            
    except requests.exceptions.HTTPError as err:
        print(f"Errore HTTP durante la richiesta a Geoapify: {err}")
    except Exception as e:
        print(f"Errore generico: {e}")