import requests

def determina_tipo_area_e_raggio_overpass(lat: float, lng: float) -> tuple[str, float]:
    """
    Interroga Overpass API (OpenStreetMap) attorno a un punto (lat, lng) 
    cercando i tag di landuse o natural nel raggio di 300 metri per 
    classificare l'area in urbana o rurale e definire il raggio.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    overpass_query = f"""
    [out:json][timeout:10];
    (
      way(around:300,{lat},{lng})["landuse"];
      relation(around:300,{lat},{lng})["landuse"];
      way(around:300,{lat},{lng})["natural"];
      relation(around:300,{lat},{lng})["natural"];
      way(around:300,{lat},{lng})["building"];
      relation(around:300,{lat},{lng})["building"];
    );
    out tags;
    """

    headers = {
        'User-Agent': 'TesiProtezioneCivileBot/1.0 (Contatto: email@studium.unict.it)'
    }
    
    try:
        print(f"[OVERPASS] Interrogazione in corso per le coordinate ({lat}, {lng})...")
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            
            tipi_elementi = []
            edifici_count = 0
            
            for el in elements:
                tags = el.get("tags", {})
                if "landuse" in tags:
                    tipi_elementi.append(tags["landuse"])
                if "natural" in tags:
                    tipi_elementi.append(tags["natural"])
                if "building" in tags:
                    edifici_count += 1
                
            print(f"[OVERPASS] Trovati landuse: {tipi_elementi}, Edifici contati: {edifici_count}")
            # Se c'è un'alta concentrazione di edifici attorno, 
            # escludiamo categoricamente che sia rurale, anche in presenza di qualche macchia verde.
            if edifici_count > 15 or "commercial" in tipi_elementi or "retail" in tipi_elementi:
                return "urbana", 500.0

            # Classificazione rurale
            # (richiede landuse agricoli o boschivi estesi, ignorando semplici aiuole o prati isolati, la spiaggia, zona costiera)
            rural_landuses = ["farmland", "farmyard", "forest", "wood", "heath", "beach", "recreation_ground", "campsite", "scrub", "dune"]
            if any(t in rural_landuses for t in tipi_elementi) or edifici_count < 15:
                return "rurale", 3000.0

        # Default se non troviamo nulla di specifico
        return "urbana", 500.0

    except Exception as e:
        print(f"[AVVISO] Eccezione durante la chiamata a Overpass: {e}. Uso default urbano (500m).")
        return "urbana", 500.0