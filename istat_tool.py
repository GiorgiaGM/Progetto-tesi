import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def get_demographic_context(lat: float, lng: float, raggio_metri: float, tipo_area: str) -> dict:
    """
    Interroga la mappa ISTAT e somma la popolazione residente 
    usando un raggio dinamico derivato da Overpass API (urbana/suburbana/rurale).
    """
    shapefile_folder = r"C:\Users\user\Downloads\R19_21\SHP"
    excel_data_2023 = r"C:\Users\user\Downloads\Comuni_2023\Comuni_2023\Catania_2023_sezioni.xlsx"

    try:
        # 1. Caricamento dello Shapefile
        if os.path.isdir(shapefile_folder):
            file_shp = [f for f in os.listdir(shapefile_folder) if f.endswith(".shp")]
            full_shape_path = os.path.join(shapefile_folder, file_shp[0])
        else:
            full_shape_path = shapefile_folder

        gdf_geo = gpd.read_file(full_shape_path)
        crs_nativo = gdf_geo.crs
        gdf_geo["SEZ21_ID"] = gdf_geo["SEZ21_ID"].astype(str)

        # 2. Caricamento del file Excel ISTAT
        df_2023 = pd.read_excel(excel_data_2023, sheet_name="Catania_2023_sezioni")
        df_2023["SEZ21_ID"] = df_2023["SEZ21_ID"].astype(str)
        df_2023_filtered = df_2023[["SEZ21_ID", "P1", "PF1"]]

        # 3. Fusione degli attributi
        merged_gdf = gdf_geo.merge(df_2023_filtered, on="SEZ21_ID", how="inner")
        merged_gdf["P1"] = merged_gdf["P1"].fillna(0).astype(int)
        merged_gdf["PF1"] = merged_gdf["PF1"].fillna(0).astype(int)
        merged_gdf["EDI21"] = merged_gdf["EDI21"].fillna(0).astype(int)

        # 4. Creazione del punto e proiezione nel sistema metrico nativo
        punto_wgs84 = gpd.GeoSeries([Point(lng, lat)], crs="EPSG:4326")
        punto_metrico = punto_wgs84.to_crs(crs_nativo).iloc[0]

        # 5. Generazione del buffer circolare basato sul raggio dinamico
        area_buffer = punto_metrico.buffer(raggio_metri)

        # 6. Filtraggio delle sezioni che intersecano il buffer
        sezioni_nel_raggio = merged_gdf[merged_gdf.intersects(area_buffer)]

        # Fallback di sicurezza
        if sezioni_nel_raggio.empty:
            indice_piu_vicino = merged_gdf.distance(punto_metrico).idxmin()
            sezioni_nel_raggio = merged_gdf.loc[[indice_piu_vicino]]

        # 7. Somma dei valori demografici
        tot_popolazione = int(sezioni_nel_raggio["P1"].sum())
        tot_famiglie = int(sezioni_nel_raggio["PF1"].sum())
        tot_edifici = int(sezioni_nel_raggio["EDI21"].sum())
        num_sezioni_coinvolte = len(sezioni_nel_raggio)

        return {
            "stato_connessione": "SUCCESS",
            "anno_dati_demografici": 2023,
            "tipo_area": tipo_area,
            "raggio_analisi_metri": raggio_metri,
            "sezioni_coinvolte": num_sezioni_coinvolte,
            "popolazione_residente_totale": tot_popolazione,
            "famiglie_residenti_totale": tot_famiglie,
            "edifici_presenti_totale": tot_edifici,
            "densita_antropica": (
                "ALTA" if tot_popolazione > 1500 
                else "MEDIO" if tot_popolazione > 400 
                else "BASSO"
            ),
        }

    except Exception as e:
        return {
            "stato_connessione": "ERROR",
            "errore": f"Errore elaborazione locale: {str(e)}",
        }


if __name__ == "__main__":
    # Test con coordinate di esempio (es. Playa)
    LAT_TEST = 37.44954834129635
    LNG_TEST = 15.08518378674863

    print("Avvio del test di verifica ISTAT con Overpass API...")
    risultato = get_demographic_context(lat=LAT_TEST, lng=LNG_TEST,raggio_metri=500.0, tipo_area="urbana")

    print("\n--- RISULTATO DEL TEST ---")
    for chiave, valore in risultato.items():
        print(f"{chiave}: {valore}")