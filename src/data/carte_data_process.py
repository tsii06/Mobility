from decimal import Decimal

import pandas as pd
import geopandas as gpd

from sqlalchemy import func

from src.data.utils import loadGeojson, get_session

from sqlalchemy import MetaData, Table, select

def get_merged_geo_population_data():
    gdf_geojson = loadGeojson()  # Charger les données GeoJSON
    session = get_session()  # Ouvrir une session
    metadata = MetaData()  # Métadonnées pour la table

    # Charger la vue population_view depuis la base de données
    population_view = Table('vue_population_par_commune', metadata, autoload_with=session.bind)

    # Créer la requête pour obtenir la somme de la population par commune
    query = (
        select(
            population_view.c.nom_commune,  # ou population_view.c.identifiant_commune selon votre besoin
            func.sum(population_view.c.total_population).label('total_population')
        )
        .group_by(population_view.c.nom_commune)  # ou group_by(population_view.c.identifiant_commune)
    )

    # Exécuter la requête et récupérer les résultats
    result = session.execute(query).fetchall()

    # Vérifier les colonnes disponibles dans les résultats
    df_population = pd.DataFrame(result, columns=['nom_commune', 'total_population'])

    # Convertir 'nom_commune' et 'ADM3_EN' en chaînes de caractères minuscules pour garantir la correspondance
    df_population['nom_commune'] = df_population['nom_commune'].astype(str).str.lower()
    gdf_geojson['ADM3_EN'] = gdf_geojson['ADM3_EN'].astype(str).str.lower()

    # Fusionner les données GeoJSON et population avec une jointure gauche basée sur gdf_geojson
    gdf_merged = gdf_geojson.merge(df_population, how='left', left_on='ADM3_EN', right_on='nom_commune')

    # Fermer la session
    session.close()

    # Convertir les objets Decimal en float pour éviter l'erreur JSON
    for col in gdf_merged.select_dtypes(include=['object']).columns:
        if gdf_merged[col].apply(lambda x: isinstance(x, Decimal)).any():
            gdf_merged[col] = gdf_merged[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

    # Calculer la moyenne de la population, arrondir et convertir en entier
    if 'total_population' in gdf_merged.columns:
        mean_population = int(round(gdf_merged['total_population'].mean(skipna=True)))  # Calculer et arrondir la moyenne
        gdf_merged['total_population'] = gdf_merged['total_population'].fillna(mean_population)  # Remplir les valeurs manquantes avec la moyenne

    return gdf_merged


def get_volume_deplacement_route():
    metadata = MetaData()
    session = get_session()

    try:
        vue = Table('vue_volume_deplacement_par_route', metadata, autoload_with=session.bind)
        query = select(vue)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        df['id_osm'] = df['id_osm'].astype('int32')
        gdf = gpd.read_file(r"data/Antananarivo_voiries_primaires-secondaires-tertiaire.geojson")
        gdf.loc[:, 'osm_id'] = gdf['osm_id'].astype('int32')
        gdf = gdf.to_crs(epsg=3857)
        gdf['centroid'] = gdf.centroid
        gdf_centroids = gdf[['osm_id', 'centroid']].copy()  # Créer une copie explicite
        gdf_centroids.loc[:, 'centroid'] = gdf_centroids['centroid'].to_crs(epsg=4326)
        df = df.merge(gdf_centroids, left_on='id_osm', right_on='osm_id', how='left')

        return df

    except Exception as e:
        print(f"Erreur lors de l'accès à la vue ou au GeoJSON : {e}")
        return None

