import json

import geopandas as gpd
import pandas as pd
import plotly.graph_objs as go
import matplotlib.colors as mcolors

from src.data.ETL.extract_geojson_data import transform_coordinate_point_noir


def create_density_carte(geo_population_data):
    print(f"Nombre de lignes dans gdf_merged : {len(geo_population_data)}")
    """Crée une carte choroplèthe pour la densité de population."""
    return go.Choroplethmapbox(
        geojson=json.loads(geo_population_data.to_json()),
        locations=geo_population_data['ADM3_EN'],
        z=geo_population_data['total_population'],
        colorscale='YlOrRd',
        marker_opacity=0.6,
        marker_line_width=1,
        featureidkey='properties.ADM3_EN',
        marker_line_color='black',
        hoverinfo='text',
        hovertext=geo_population_data['ADM3_EN'] + '<br>Population totale: ' + geo_population_data['total_population'].astype(str),
        showscale=False
    )


def create_default_carte(geo_population_data):
    """Crée une carte par défaut avec un thème grisé."""
    return go.Choroplethmapbox(
        geojson=geo_population_data.__geo_interface__,
        locations=geo_population_data['ADM3_EN'],
        z=[0] * len(geo_population_data),
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
        marker_opacity=0.8,
        marker_line_width=1,
        featureidkey='properties.ADM3_EN',
        marker_line_color='black',
        hoverinfo='text',
        hovertext=geo_population_data['ADM3_EN'],
        showscale=False
    )

def create_route(lats, lons):
    return go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='lines',
        line=dict(width=1.5, color='#4682B4'),
        name='Routes',
        hoverinfo='skip'
    )


def create_traffic_markers(geo_traffic_data):
    # Créer une trace pour les marqueurs de trafic

    marker_trace = go.Scattermapbox(
        lat=geo_traffic_data['centroid'].apply(lambda point: point.y),  # Latitude
        lon=geo_traffic_data['centroid'].apply(lambda point: point.x),  # Longitude
        mode='markers',
        marker=dict(
            size=20,  # Ajuster la taille en fonction du volume
            color=geo_traffic_data['total_traffic_volume'],       # Couleur en fonction du volume
            colorscale='Viridis',                    # Echelle de couleurs (jaune à rouge)
            cmin=geo_traffic_data['total_traffic_volume'].min(),
            cmax=geo_traffic_data['total_traffic_volume'].max(),
            showscale=False
        ),

        text=geo_traffic_data['total_traffic_volume'],
        name='Congestion',
        hoverinfo='text',  # Afficher uniquement le texte dans le survol
        hovertext=geo_traffic_data.apply(
            lambda
                row: f"Volume de trafic: {row['total_traffic_volume']}",
            axis=1
        )

    )
    return marker_trace


def load_and_prepare_traffic_data(geojson_path, traffic_data_function):
    gdf = gpd.read_file(geojson_path)

    # Charger les données de trafic
    df_traffic = traffic_data_function()  # Cette fonction doit retourner un DataFrame avec les volumes de trafic
    df_traffic['id_osm'] = df_traffic['id_osm'].astype('int32')  # Assurez-vous que les types sont cohérents

    # Filtrer les routes principales, secondaires et tertiaires
    gdf_filtered = gdf[gdf['highway'].isin(['primary', 'secondary', 'tertiary'])]

    # Convertir en système de coordonnées approprié
    gdf_filtered = gdf_filtered.to_crs(epsg=3857)
    gdf_filtered = gdf_filtered.to_crs(epsg=4326)

    # Fusionner les données géographiques avec les volumes de trafic
    gdf_filtered = gdf_filtered.merge(df_traffic[['id_osm', 'total_traffic_volume']], left_on='osm_id',
                                      right_on='id_osm', how='left')

    # Remplir les valeurs manquantes par 0 pour les volumes de trafic
    gdf_filtered['total_traffic_volume'] = gdf_filtered['total_traffic_volume'].fillna(0)

    return gdf_filtered
def create_route_with_traffic(geo_traffic_data):
    traces = []
    for _, row in geo_traffic_data.iterrows():
        lats, lons = [], []
        geom = row['geometry']
        if geom.geom_type == 'MultiLineString':
            for line in geom.geoms:
                lons.extend([coord[0] for coord in line.coords] + [None])
                lats.extend([coord[1] for coord in line.coords] + [None])
        elif geom.geom_type == 'LineString':
            lons.extend([coord[0] for coord in geom.coords] + [None])
            lats.extend([coord[1] for coord in geom.coords] + [None])

        if row['total_traffic_volume'] > 0:
            hover_text = (
                f"Route ID: {row['osm_id']}<br>"
                f"Volume de trafic: {row['total_traffic_volume']}"
            )
            traces.append(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(
                    width=max(row['total_traffic_volume'] / 50, 1),  # Ajuster la largeur des lignes selon le volume
                    color='blue'  # Vous pouvez ajuster la couleur ici ou ajouter une échelle de couleurs
                ),
                opacity=min(row['total_traffic_volume'] / 1000, 1),  # Ajuster l'opacité au niveau de la trace
                hoverinfo='text',
                hovertext=hover_text,
                name=row['osm_id']
            ))

    # Créer la figure
    return traces


def create_route_with_traffic_colored(geo_traffic_data):
    traces = []

    # Définir l'échelle de couleurs du jaune au rouge
    # reds_orange_yellow = mcolors.LinearSegmentedColormap.from_list('RedsOrangeYellow', ['#ffffb2', '#fd8d3c', '#de2d26'])
    reds_orange_yellow = mcolors.LinearSegmentedColormap.from_list('BlueVioletBlack',
                                                            ['#cce5ff', '#003366', '#663399', '#000000'])
    # Vérifier les types de données et convertir si nécessaire
    geo_traffic_data['total_traffic_volume'] = pd.to_numeric(geo_traffic_data['total_traffic_volume'], errors='coerce')

    # Remplacer les NaN par zéro ou une autre valeur selon le contexte de votre application
    geo_traffic_data['total_traffic_volume'].fillna(0, inplace=True)

    max_traffic_volume = geo_traffic_data['total_traffic_volume'].max()

    for _, row in geo_traffic_data.iterrows():
        lats, lons = [], []
        geom = row['geometry']
        if geom.geom_type == 'MultiLineString':
            for line in geom.geoms:
                lons.extend([coord[0] for coord in line.coords] + [None])
                lats.extend([coord[1] for coord in line.coords] + [None])
        elif geom.geom_type == 'LineString':
            lons.extend([coord[0] for coord in geom.coords] + [None])
            lats.extend([coord[1] for coord in geom.coords] + [None])

        if row['total_traffic_volume'] > 0:
            hover_text = (
                f"Route ID: {row['osm_id']}<br>"
                f"Volume de trafic: {row['total_traffic_volume']}"
            )

            # Calculer la couleur en fonction du volume de trafic
            color_scale_value = row['total_traffic_volume'] / max_traffic_volume
            color = mcolors.to_hex(reds_orange_yellow(color_scale_value))

            traces.append(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(
                    width=3,  # Ajuster la largeur des lignes selon le volume
                    color=color  # Utiliser la couleur calculée
                ),
                opacity=1,  # Ajuster l'opacité au niveau de la trace
                hoverinfo='text',
                hovertext=hover_text,
                name=row['osm_id']
            ))

    return traces

def create_traffic_markers_from_df():
    # Créer la trace pour les marqueurs de trafic
    df= transform_coordinate_point_noir()
    marker_trace = go.Scattermapbox(
        lat=df['longitude'],  # Latitude
        lon=df['latitude'],  # Longitude
        mode='markers',
        marker=dict(
            size=15,  # Taille des marqueurs
            color='black',  # Couleur des marqueurs
            showscale=False
        ),
        text=df['Name'],  # Nom des lieux
        hoverinfo='text',  # Affichage du texte au survol
    )

    return marker_trace