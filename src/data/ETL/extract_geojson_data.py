import pandas as pd
from pyproj import Transformer
import geopandas as gpd

def loadRepartitionZonale():
    # Exemple de chemin d'accès au fichier GeoJSON (à adapter en figure de votre fichier réel)
    geojson_path = r"data/limites_communes_ANTANANARIVO.geojson"

    # Charger le GeoDataFrame à partir du fichier GeoJSON
    gdf_geojson = gpd.read_file(geojson_path)

    # Vérification des systèmes de coordonnées
    if gdf_geojson.crs != "EPSG:4326":
        gdf_geojson = gdf_geojson.to_crs(epsg=4326)
    return gdf_geojson


def transform_coordinate_point_noir():
    # Charger le fichier GeoJSON en tant que GeoDataFrame
    geojson_path = r"data/Point.geojson"

    gdf = gpd.read_file(geojson_path)

    # Initialiser le transformateur pour EPSG:3857 vers EPSG:4326 (latitude/longitude)
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

    # Transformer les coordonnées
    gdf['latitude'], gdf['longitude'] = zip(*gdf.geometry.apply(lambda point: transformer.transform(point.x, point.y)))

    # Créer un DataFrame avec les colonnes pertinentes
    df = pd.DataFrame({
        'Name': gdf['Name'],
        'latitude': gdf['latitude'],
        'longitude': gdf['longitude']
    })
    return df