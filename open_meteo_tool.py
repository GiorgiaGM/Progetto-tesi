import requests
import json

def get_weather_context(lat: float, lon: float) -> dict:
    """
    Interrogo l'API aperta di Open-Meteo per estrarre le metriche ambientali 
    necessarie al Reasoning Layer.
    
    :param lat: Latitudine dell'evento d'emergenza
    :param lon: Longitudine dell'evento d'emergenza
    :return: Dizionario strutturato con i parametri meteo critici
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,wind_direction_10m&"
        f"hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability&"
        f"forecast_days=1&"
        f"timezone=auto"
    )
    
    try:
        print(f"[METEO] Interrogazione Open-Meteo per coordinate: ({lat}, {lon})...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current_data = data.get("current", {})

            
            # Costruzione del payload finale
            meteo = {
                "stato_connessione": "SUCCESS",
                "condizioni_attuali": {
                    "temperatura_c": current_data.get("temperature_2m", 0.0),
                    "umidita_relativa_percentuale": current_data.get("relative_humidity_2m", 0),
                    "pioggia_mm": current_data.get("rain", 0.0),
                    "velocita_vento_kmh": current_data.get("wind_speed_10m", 0.0),
                    "direzione_vento_gradi": current_data.get("wind_direction_10m", 0)
                }
            }
            return meteo
        else:
            return {
                "stato_connessione": "ERROR",
                "errore": f"Server risposto con codice {response.status_code}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "stato_connessione": "ERROR",
            "errore": f"Impossibile connettersi a Open-Meteo: {str(e)}"
        }


# TEST DI VERIFICA (Simulazione Emergenza a Catania)

if __name__ == "__main__":
    LAT_CATANIA = 37.4722
    LON_CATANIA = 15.0644
    
    risultato_meteo = get_weather_context(LAT_CATANIA, LON_CATANIA)
    
    print("\n PAYLOAD DI RITORNO PER L'AGENTE CENTRALIZZATO")
    print(json.dumps(risultato_meteo, indent=4, ensure_ascii=False))
