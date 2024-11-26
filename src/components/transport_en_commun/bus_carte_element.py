import json
import os
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from pyproj import CRS
from dash import Dash, dcc, html
import plotly.express as px  # Pour obtenir une palette de couleurs
import xml.etree.ElementTree as ET
from src.data.bus_line_data_process import convert_utm_to_latlon, extract_lat_lon


def process_transport_geometry(combined_dataframe):
    """Prépare le DataFrame complet avec les centroïdes pour chaque ligne de transport_en_commun."""

    # Définir le CRS UTM actuel (EPSG:32738 pour UTM zone 38S)
    utm_crs = CRS.from_epsg(32738)

    # Convertir les données de UTM à latitude/longitude
    combined_dataframe = gpd.GeoDataFrame(combined_dataframe, geometry='geometry', crs=utm_crs)
    combined_dataframe = convert_utm_to_latlon(combined_dataframe, utm_crs)

    # Filtrer uniquement les géométries de type LineString
    combined_dataframe = combined_dataframe[combined_dataframe.geometry.type == 'LineString']

    # Projeter les géométries dans un CRS projeté (par exemple, UTM) pour calculer les centroïdes correctement
    projected_crs = CRS.from_epsg(3857)  # Web Mercator projection
    projected_gdf = combined_dataframe.to_crs(projected_crs)

    # Calculer les centroïdes dans le CRS projeté
    centroids = projected_gdf.geometry.centroid

    # Revenir au CRS géographique pour la visualisation
    combined_dataframe['centroid_lon'] = centroids.to_crs(CRS.from_epsg(4326)).x
    combined_dataframe['centroid_lat'] = centroids.to_crs(CRS.from_epsg(4326)).y

    return combined_dataframe

def generate_carte_ligne(prepared_dataframe, indicateur, couleur, bus_lines=None):
    """Crée une carte Mapbox en utilisant les données préparées et les lignes de transport_en_commun spécifiées, ou toutes les lignes si aucune sélection n'est faite."""

    # Si bus_lines est None ou vide, afficher toutes les lignes de transport_en_commun
    if bus_lines:
        filtered_dataframe = prepared_dataframe[prepared_dataframe['numero_ligne'].isin(bus_lines)]
    else:
        filtered_dataframe = prepared_dataframe  # Ne pas filtrer, afficher toutes les lignes

    # Si le DataFrame filtré est vide, ne pas générer de carte
    if filtered_dataframe.empty:
        print("Aucune donnée disponible pour les lignes de transport_en_commun spécifiées.")
        return None

    # Palette de couleurs personnalisée en fonction de l'indicateur
    color_map = {}
    if indicateur in filtered_dataframe.columns:
        # Remplacer les NaN par une valeur par défaut (par exemple, 0 ou une valeur de substitution)
        filtered_dataframe[indicateur].fillna(0, inplace=True)

        # Agréger les valeurs de l'indicateur par ligne
        aggregated_values = filtered_dataframe.groupby('numero_ligne')[indicateur].mean()

        # Supprimer les éventuelles valeurs NaN après agrégation
        aggregated_values = aggregated_values.dropna()

        # Vérifier si le DataFrame agrégé est vide après suppression des NaN
        if aggregated_values.empty:
            print("Aucune valeur valide pour l'indicateur spécifié après agrégation.")
            return None

        # Normaliser les valeurs agrégées pour les mapper entre 0 et 1
        min_val, max_val = aggregated_values.min(), aggregated_values.max()
        normalized_values = (aggregated_values - min_val) / (max_val - min_val + 1e-9)  # Ajouter un epsilon pour éviter les divisions par zéro

        # Palette de couleurs personnalisée (vert, jaune, rouge, noir) avec seuils
        custom_colorscale = ["green", "orange", "red", "black"]

        # Mapping des couleurs en fonction des valeurs normalisées
        color_map = {
            numero_ligne: custom_colorscale[min(int(val * len(custom_colorscale)), len(custom_colorscale) - 1)]
            for numero_ligne, val in normalized_values.items()
        }

        # **Filtrage par couleur sélectionnée**
        if couleur in custom_colorscale:
            lignes_a_conserver = [num for num, col in color_map.items() if col == couleur]
            filtered_dataframe = filtered_dataframe[filtered_dataframe['numero_ligne'].isin(lignes_a_conserver)]

    else:
        # Utiliser une palette par défaut si l'indicateur n'est pas présent
        unique_lignes = filtered_dataframe['numero_ligne'].unique()
        color_map = {num: px.colors.qualitative.Plotly[idx % len(px.colors.qualitative.Plotly)]
                     for idx, num in enumerate(unique_lignes)}

    # Créer la liste des traces de lignes de transport_en_commun pour Mapbox
    ligne = []

    # Grouper par ligne de transport_en_commun ('numero_ligne') et ajouter un tracé par groupe
    grouped = filtered_dataframe.groupby('numero_ligne')

    for taxibe_lin, group in grouped:
        lats, lons = [], []
        text_info = []  # Liste pour stocker les informations de texte pour chaque segment
        customdata = []  # Liste pour stocker les données supplémentaires comme osm_id

        for _, row in group.iterrows():
            lat, lon = extract_lat_lon(row['geometry'])
            lats.extend(lat)
            lons.extend(lon)

            # Ajouter une information de texte personnalisée pour chaque ligne
            if indicateur in row:
                text_info.extend([f"Ligne {taxibe_lin}, {indicateur}: {row[indicateur]}" for _ in range(len(lat))])
            else:
                text_info.extend([f"Ligne {taxibe_lin}" for _ in range(len(lat))])

            customdata.extend([row['osm_id']] * len(lat))  # Ajouter osm_id pour chaque point de la ligne

        # Couleur en fonction de l'indicateur agrégé pour chaque ligne de transport_en_commun
        line_color = color_map.get(taxibe_lin, "rgb(0, 0, 0)")  # Défaut au noir si pas de couleur

        ligne.append(go.Scattermapbox(
            lon=lons,
            lat=lats,
            mode='lines',
            line=dict(width=2, color=line_color),  # Couleur unique pour chaque ligne de transport_en_commun
            name=f"Bus Route {taxibe_lin}",
            hoverinfo='text',
            text=text_info,
            customdata=customdata,  # Inclure osm_id pour chaque point
        ))

    return ligne



def create_bus_stops_map_from_xml(xml_path):
    # Lire le fichier XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extraire les informations des arrêts de transport_en_commun
    bus_stops = []
    for route in root.findall('route'):
        for stop in route.findall('stop'):
            name = stop.get('name')
            coordinates = stop.get('coordinates')
            osm_id = stop.get('osm_id')

            # Vérifier si les coordonnées sont valides (non 'None')
            if coordinates and coordinates.lower() != 'none':
                lon, lat = map(float, coordinates.split(', '))
                bus_stops.append({
                    'name': name,
                    'coordinates': (lon, lat),
                    'osm_id': osm_id
                })

    # Extraire les coordonnées et les noms
    latitudes = [stop['coordinates'][1] for stop in bus_stops]
    longitudes = [stop['coordinates'][0] for stop in bus_stops]
    names = [stop['name'] if stop['name'] else f"Bus Stop" for stop in bus_stops]

    # Créer une seule trace pour tous les arrêts
    return go.Scattermapbox(
        lon=longitudes,  # Liste des longitudes
        lat=latitudes,  # Liste des latitudes
        mode='markers',
        marker=go.scattermapbox.Marker(size=9, color='blue'),  # Couleur uniforme pour tous les markers
        text=names,  # Nom de l'arrêt de transport_en_commun
        name='Bus Stops'
    )


def generate_graphique_en_barre(df, indicateur):
    df['numero_ligne'] = df['numero_ligne'].astype(str)

    # Vérification que l'indicateur existe dans le DataFrame
    if indicateur not in df.columns:
        raise ValueError(f"L'indicateur {indicateur} n'existe pas dans le DataFrame.")

    # Traductions en langage naturel pour les axes
    titres_axes = {
        'nombre_passager_jour': 'Nombre de Passagers par Jour',
        'distance_primus_terminus': 'Distance Primus-Terminus (km)',
        'nombre_bus_jour': 'Nombre de Bus par Jour',
        'nombre_rotation': 'Nombre de Rotations par Jour',
        'consommation_jour': 'Consommation Moyenne par Jour (litres)'
    }

    # Définir le titre des axes
    yaxis_title = titres_axes.get(indicateur,
                                  indicateur)  # Utilise le titre en langage naturel ou l'indicateur par défaut

    # Génération du graphique (barres pour ce type de comparaison)
    fig = px.bar(
        df,
        x='numero_ligne',
        y=indicateur,
        title=f"Comparaison des lignes de transport_en_commun pour {yaxis_title}",
        labels={'numero_ligne': 'Lignes de transport_en_commun', indicateur: yaxis_title}
    )

    # Personnalisation des axes
    fig.update_layout(
        xaxis_title='Numéro de Ligne de Bus',
        yaxis_title=yaxis_title,
        title={
            'text': f"Graphique de l'indicateur : {yaxis_title}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig


def generate_graphique_en_nuage_point(df, indicateur_x, indicateur_y):
    # Traductions en langage naturel pour les axes
    titres_axes = {
        'nombre_passager_jour': 'Nombre de Passagers par Jour',
        'distance_primus_terminus': 'Distance Primus-Terminus (km)',
        'nombre_bus_jour': 'Nombre de Bus par Jour',
        'nombre_rotation': 'Nombre de Rotations par Jour',
        'consommation_jour': 'Consommation Moyenne par Jour (litres)'
    }

    # Vérification que les deux indicateurs existent dans le DataFrame
    if indicateur_x not in df.columns:
        raise ValueError(f"L'indicateur {indicateur_x} n'existe pas dans le DataFrame.")
    if indicateur_y not in df.columns:
        raise ValueError(f"L'indicateur {indicateur_y} n'existe pas dans le DataFrame.")

    # Traductions des titres pour les axes
    xaxis_title = titres_axes.get(indicateur_x, indicateur_x)
    yaxis_title = titres_axes.get(indicateur_y, indicateur_y)

    # Génération du scatter plot
    fig = px.scatter(
        df,
        x=indicateur_x,
        y=indicateur_y,
        title=f"Relation entre {xaxis_title} et {yaxis_title}",
        labels={indicateur_x: xaxis_title, indicateur_y: yaxis_title},
        hover_data=['numero_ligne']
    )

    # Personnalisation des axes et du fond
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        title={
            'text': f"Relation entre {xaxis_title} et {yaxis_title}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        plot_bgcolor='rgba(0,0,0,0)',  # Fond transparent
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig
