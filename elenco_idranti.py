import math


IDRANTI_CATANIA = [
    {"indirizzo": "Via Galatioto 178", "riferimento": "Pressi ufficio postale", "lat": 37.52891667, "lng": 15.10211111, "pressione_bar": 4.0, "portata_lm": 300, "accessibilita": "Buona"},
    {"indirizzo": "Via Anapo fronte civ.16", "riferimento": "Ang. Via Borghetti", "lat": 37.52241667, "lng": 15.11066667, "pressione_bar": 6.0, "portata_lm": 360, "accessibilita": "Buona"},
    {"indirizzo": "Via Messina 348/A", "riferimento": "Ang. Via Wrzì", "lat": 37.52191667, "lng": 15.10775000, "pressione_bar": 5.2, "portata_lm": 325, "accessibilita": None},
    {"indirizzo": "Via del Rotolo", "riferimento": "50mt da Viale A. Aragona", "lat": 37.52402778, "lng": 15.11569444, "pressione_bar": 6.0, "portata_lm": 375, "accessibilita": None},
    {"indirizzo": "Via V. Giuffrida 76", "riferimento": "Ang. Corso delle Provincie", "lat": 37.51911111, "lng": 15.09155556, "pressione_bar": 4.2, "portata_lm": 290, "accessibilita": None},
    {"indirizzo": "Via Acitrezza", "riferimento": None, "lat": 37.52286111, "lng": 15.10300000, "pressione_bar": 4.6, "portata_lm": 350, "accessibilita": None},
    {"indirizzo": "Via Vescovo Maurizio", "riferimento": "Fronte Ist. Galilei", "lat": 37.53475000, "lng": 15.10508333, "pressione_bar": 4.0, "portata_lm": 270, "accessibilita": None},
    {"indirizzo": "Via Savasta 70", "riferimento": "Chiesa S. Lucia", "lat": 37.52666667, "lng": 15.10669444, "pressione_bar": 5.0, "portata_lm": 300, "accessibilita": None},
    {"indirizzo": "Via Mons. Domenico Orlando 11", "riferimento": "Davanti Bar", "lat": 37.53316667, "lng": 15.10858333, "pressione_bar": 4.0, "portata_lm": 220, "accessibilita": None},
]


def haversine(lat1, lon1, lat2, lon2):
    """Calcola la distanza in metri tra due punti geografici."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def trova_idranti_vicini(lat_evento: float, lng_evento: float, raggio_metri: float = 500) -> list:
    """
    Trova gli idranti entro il raggio con accessibilità 'Buona' o 'Ottima',
    restituendo i risultati ordinati per vicinanza.
    """
    risultati = []
    accessibilita_valide = ["Buona", "Ottima"]
    for i in IDRANTI_CATANIA:
        if i.get("accessibilita") in accessibilita_valide:
            distanza = haversine(lat_evento, lng_evento, i["lat"], i["lng"])
            if distanza <= raggio_metri:
                risultati.append({
                    **i,
                    "distanza_metri": round(distanza)
                })
    risultati_ordinati = sorted(risultati, key=lambda x: x["distanza_metri"])
    
    return risultati_ordinati


if __name__ == "__main__":
    lat_test, lng_test = 37.5074, 15.0873

    print("=" * 50)
    print(f"TEST IDRANTI (Ricerca attorno a lat: {lat_test}, lng: {lng_test})")
    print("=" * 50)

    risultato = trova_idranti_vicini(lat_test, lng_test, raggio_metri=500)

    import json
    print(json.dumps(risultato, indent=4, ensure_ascii=False))
    print(f"\nTrovati {len(risultato)} idranti entro 500m")