import os
import geopandas as gpd
import pandas as pd
from pyproj import CRS

from sqlalchemy import MetaData, Table, select, func

import re

from src.data.utils import get_session


def get_bus_lines_dropdown_options():
    metadata = MetaData()
    session = get_session()

    try:
        vue = Table('lignes', metadata, autoload_with=session.bind)
        query = select(vue)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        options = [{'label': row['numero_ligne'], 'value': row['numero_ligne']} for _, row in df.iterrows()]
        return options

    finally:
        session.close()



def get_all_ligne_from_geojson():
    directory_path = r"data/Ligne"
    # Initialiser une liste vide pour stocker chaque GeoDataFrame
    gdf_list = []

    # Colonnes que nous souhaitons conserver pour la visualisation
    columns_to_keep = ['fid_grandt', 'osm_id', 'fclass', 'name', 'taxibe_lin', 'km', 'geometry']

    # Créer un set pour suivre les lignes de transport_en_commun uniques
    lignes_unique = set()

    # Parcourir tous les fichiers dans le répertoire spécifié
    for filename in os.listdir(directory_path):
        if filename.endswith(".geojson"):  # Filtrer les fichiers GeoJSON
            file_path = os.path.join(directory_path, filename)
            try:
                # Lire le fichier GeoJSON en tant que GeoDataFrame
                gdf = gpd.read_file(file_path)

                # Harmoniser les noms des colonnes en minuscules
                gdf.columns = gdf.columns.str.lower()

                # Vérifier si les colonnes nécessaires existent et filtrer
                available_columns = [col for col in columns_to_keep if col in gdf.columns]
                gdf = gdf[available_columns]

                # Nettoyer la colonne 'taxibe_lin' pour ne garder que les chiffres
                if 'taxibe_lin' in gdf.columns:
                    gdf['taxibe_lin'] = gdf['taxibe_lin'].apply(lambda x: re.sub(r'\D', '', str(x)))

                # Filtrer les lignes déjà présentes
                gdf = gdf[~gdf['taxibe_lin'].isin(lignes_unique)]

                # Ajouter les nouvelles lignes de transport_en_commun au set
                lignes_unique.update(gdf['taxibe_lin'].unique())

                # Ajouter le GeoDataFrame filtré à la liste
                gdf_list.append(gdf)

            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {filename}: {e}")

    # Concaténer tous les GeoDataFrames en un seul DataFrame
    if gdf_list:
        combined_gdf = pd.concat(gdf_list, ignore_index=True)
        return combined_gdf
    else:
        print("Aucun fichier GeoJSON trouvé ou aucun fichier valide.")
        return None


def get_all_ligne_from_database():
    session = get_session()
    metadata = MetaData()

    try:
        # Chargement de la vue 'view_cooperative_ligne_antenne'
        vue = Table('vue_cooperative_ligne_antenne', metadata, autoload_with=session.bind)

        # Requête pour sélectionner toutes les lignes
        query = select(vue)

        # Exécution de la requête
        result = session.execute(query)

        # Conversion en DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

    finally:
        session.close()


def get_geo_data_all_ligne():
    # Charger les deux DataFrames
    geojson_df = get_all_ligne_from_geojson()
    db_df = get_all_ligne_from_database()

    # Vérifier que les DataFrames sont chargés correctement
    if geojson_df is None or db_df is None:
        print("Erreur lors du chargement des données.")
        return None

    # Harmoniser les noms des colonnes pour faciliter la jointure
    geojson_df = geojson_df.rename(columns={'taxibe_lin': 'numero_ligne'})

    # Convertir 'numero_ligne' en chaînes de caractères pour les deux DataFrames
    geojson_df['numero_ligne'] = geojson_df['numero_ligne'].astype(str)
    db_df['numero_ligne'] = db_df['numero_ligne'].astype(str)

    # Joindre les deux DataFrames sur la colonne 'numero_ligne'
    combined_df = pd.merge(geojson_df, db_df, on='numero_ligne', how='left')

    return combined_df


# Convertir les coordonnées UTM en latitude et longitude
def convert_utm_to_latlon(gdf, utm_crs):
    wgs84_crs = CRS.from_epsg(4326)
    gdf = gdf.to_crs(wgs84_crs)

    return gdf


# Fonction pour extraire les coordonnées de latitude et longitude uniquement pour les LineString
def extract_lat_lon(geom):
    lats, lons = [], []
    if geom.geom_type == 'LineString':
        lons.extend([coord[0] for coord in geom.coords] + [None])
        lats.extend([coord[1] for coord in geom.coords] + [None])
    return lats, lons



def enrich_lignes_data():
    # Récupère les données de base de la vue
    df = get_all_ligne_from_database()

    # Définir les constantes et valeurs par défaut
    frais_par_passager = 600
    prix_carburant_par_litre = 4900
    amortissement_journalier = 20000
    salaire_chauffeur_receveur = 30000
    capacite_par_defaut = 28  # Capacité par défaut d'un transport_en_commun

    # Ajouter une colonne de capacité de transport_en_commun par défaut
    df['capacite_bus'] = capacite_par_defaut

    # Convertir les colonnes en float pour éviter les erreurs de type avec decimal.Decimal
    float_columns = [
        'distance_aller_retour', 'distance_primus_terminus', 'nombre_rotation',
        'nombre_arret', 'consomation_jour', 'nombre_passager_jour', 'nombre_bus_jour', 'nombre_vehicule',
        'heure_exploitation'
    ]
    for col in float_columns:
        if col in df.columns:
            df[col] = df[col].astype(float)

    # Vérifier et éviter les divisions par zéro
    df['distance_aller_retour'] = df['distance_aller_retour'].replace(0, pd.NA)
    df['distance_primus_terminus'] = df['distance_primus_terminus'].replace(0, pd.NA)
    df['nombre_rotation'] = df['nombre_rotation'].replace(0, pd.NA)
    df['nombre_arret'] = df['nombre_arret'].replace(0, pd.NA)

    # Calculs des indicateurs basés sur les colonnes de la vue et les constantes

    # 1. Coût de carburant par jour en fonction de la consommation et de la distance parcourue
    df['cout_carburant_par_jour'] = (
        (df['consomation_jour'] / 100) * df['distance_aller_retour'] * prix_carburant_par_litre * df['nombre_rotation']
    )

    # 2. Revenu total par jour (frais par passager * nombre de passagers par jour)
    df['revenu_par_jour'] = (frais_par_passager * df['nombre_passager_jour'])/df['nombre_bus_jour']

    # 3. Autres coûts d'exploitation fixes (amortissement et salaires)
    df['autres_couts_exploitation'] = amortissement_journalier + salaire_chauffeur_receveur

    # 4. Coût d'exploitation total par jour (coût du carburant + autres coûts d'exploitation)
    df['cout_exploitation_total'] = (
        df['cout_carburant_par_jour'] + df['autres_couts_exploitation']
    )

    # 5. Rentabilité par jour (revenu total - coût d'exploitation total)
    df['rentabilite_par_jour'] = df['revenu_par_jour'] - df['cout_exploitation_total']

    # 6. Coût par rotation
    df['cout_par_rotation'] = df['cout_carburant_par_jour'] / df['nombre_rotation'].replace(0, pd.NA)

    # 7. Coût par passager (ajusté pour le coût d'exploitation total)
    df['cout_par_passager'] = df['cout_exploitation_total'] / (df['nombre_passager_jour'].replace(0, pd.NA)/df['nombre_bus_jour'])


    # 8. Ratio de remplissage
    df['ratio_remplissage'] = (df['nombre_passager_jour'] / (
        df['nombre_vehicule'] * df['capacite_bus'] * df['nombre_rotation'])*100
    ).replace(0, pd.NA)

    # Calculs supplémentaires
    # 9. Bus par kilomètre entre le primus et le terminus
    df['bus_par_km'] = df['nombre_vehicule'] / df['distance_primus_terminus'].replace(0, pd.NA)

    # 10. Distance moyenne par arrêt
    df['distance_par_arret'] = df['distance_primus_terminus'] / df['nombre_arret'].replace(0, pd.NA)

    df['duree_rotation'] = (df['heure_exploitation'] * 60) / df['nombre_rotation'].replace(0, pd.NA)

    # Retourne le DataFrame enrichi avec les nouveaux indicateurs
    return df

