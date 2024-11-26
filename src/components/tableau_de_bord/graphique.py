import numpy as np
from dash import dcc, html, dash_table
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from src.data.carte_data_process import get_merged_geo_population_data
from src.data.graphique_data_process import get_volume_deplacements, \
    get_nombre_vehicules_par_zone, get_od_count, get_population_par_commune

# Chargement des données
gdf_merged = get_merged_geo_population_data()

# Ce fonction permet de genere un graphique de densite
def generate_population_histogram(noms_communes=None):
    # Obtenir les données de population par commune en appelant une fonction similaire à `get_population_par_commune`
    df_population = get_population_par_commune(noms_communes)

    components = []

    # Si une seule commune est sélectionnée, on crée un pie chart pour cette commune
    if noms_communes and len(noms_communes) == 1:
        commune_nom = noms_communes[0]
        commune_nom = commune_nom.lower()  # Transformation du nom de la commune en minuscule

        # Filtrer les données pour la commune sélectionnée
        df_commune = df_population[df_population['nom_commune'].str.lower() == commune_nom]
        df_commune = df_commune[df_commune['total_population'] > 0]  # Exclure les valeurs nulles ou égales à 0

        fig_pie = go.Figure(data=[
            go.Pie(
                labels=["Population"],
                values=df_commune['total_population'],
                textinfo='label+percent',
                insidetextorientation='radial'
            )
        ])

        fig_pie.update_layout(
            title=f"Répartition de la population dans la commune {commune_nom.capitalize()}",
            margin=dict(l=50, r=50, t=100, b=50)
        )

        components.append(dcc.Graph(id='population-pie-chart', figure=fig_pie, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['toImage', 'zoom2d', 'pan2d'],
            'scrollZoom': False
        }))

    else:
        fig_bar = go.Figure()

        # Calculer la population totale par commune
        df_totals = df_population.groupby('nom_commune')['total_population'].sum().reset_index()

        fig_bar.add_trace(go.Bar(
            x=df_totals['nom_commune'],  # Nom des communes sur l'axe x
            y=df_totals['total_population'],  # Population sur l'axe y
            text=df_totals['total_population'],  # Texte de la population totale
            textposition='auto'  # Position automatique du texte
        ))

        # Mise à jour du layout du bar chart
        fig_bar.update_layout(
            title='Nombre de population par commune',
            xaxis_title='Commune',
            yaxis_title='Population',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=100, b=50),
            xaxis=dict(tickangle=-45),
        )

        components.append(dcc.Graph(id='population-bar-chart', figure=fig_bar, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['toImage', 'zoom2d', 'pan2d'],
            'scrollZoom': False
        }))

    # Retourner le Div contenant le titre et le graphique
    return html.Div([
        html.Div([
            html.I(className='fas fa-chart-bar', style={'margin-right': '1rem', 'font-size': '1.5rem'}),
            html.H3("Population par Commune", style={'display': 'inline-block', 'textAlign': 'center', 'margin': 0},
                    id="title-population-par-commune"),
            html.Span(
                html.I(className='fas fa-info-circle', style={'margin-left': '0.5rem', 'font-size': '1rem'}),
                id='info-icon-population',  # ID correspondant pour le Popover
                style={'cursor': 'pointer'}
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Détails sur la Visualisation - Population par Commune"),
                    dbc.PopoverBody([
                        "Cette visualisation affiche la population des communes sélectionnées.",
                        html.Br(), html.Br(),
                        html.B("Comment lire ce graphique :"),
                        html.Ul([
                            html.Li("Si une seule commune est sélectionnée, la répartition de la population est affichée sous forme de diagramme circulaire (pie chart) pour illustrer le pourcentage de la population totale."),
                            html.Li("Si plusieurs communes sont sélectionnées, le nombre de personnes dans chaque commune est affiché sous forme de diagramme à barres (bar chart), facilitant les comparaisons entre communes."),
                            html.Li("Les barres ou segments du graphique indiquent la population totale ou le pourcentage de population pour chaque commune.")
                        ]),
                        html.Br(),
                        "Ce graphique permet de comprendre la distribution de la population dans les différentes communes et d'identifier les zones les plus peuplées.",
                        html.Br(), html.Br(),
                        html.I(className="fas fa-file-alt me-2"),
                        "Source de données : AGETIPA.",
                        html.Br(),
                        html.A("Cliquez ici pour plus de détails sur les données utilisées", href="https://www.exemple.com/details_population", target="_blank", style={'color': '#007bff'})
                    ])
                ],
                id="popover-population",  # ID unique pour le Popover
                target='info-icon-population',  # Cible l'icône d'information
                trigger='hover',  # Affiche le popover au survol
                placement='right',
                style={'font-size': '0.8rem', 'max-width': '250px'}
            )
        ], className='custom-div'),
        *components
    ])

def generate_graph_deplacement(noms_zones=None):
    components = []
    df_deplacement = get_volume_deplacements(noms_zones)

    # Calculer le pourcentage de production et d'attraction par rapport au volume total
    df_deplacement['pourcentage_productions'] = (df_deplacement['total_productions'] / df_deplacement['total_volume']) * 100
    df_deplacement['pourcentage_attractions'] = (df_deplacement['total_attractions'] / df_deplacement['total_volume']) * 100

    fig_bar = go.Figure(data=[
        go.Bar(
            name='Productions (%)',
            y=df_deplacement['nom_commune'],  # Nom des zones sur l'axe y
            x=df_deplacement['pourcentage_productions'],  # Pourcentage sur l'axe x
            marker_color='rgba(31, 119, 180, 0.8)',  # Bleu pour les productions
            text=df_deplacement['pourcentage_productions'].round(2).astype(str) + '%',  # Ajout du texte avec le %
            textposition='auto',  # Position automatique du texte
            orientation='h'  # Barres horizontales
        ),
        go.Bar(
            name='Attractions (%)',
            y=df_deplacement['nom_commune'],  # Nom des zones sur l'axe y
            x=df_deplacement['pourcentage_attractions'],  # Pourcentage sur l'axe x
            marker_color='rgba(255, 127, 14, 0.8)',  # Orange pour les attractions
            text=df_deplacement['pourcentage_attractions'].round(2).astype(str) + '%',  # Ajout du texte avec le %
            textposition='auto',  # Position automatique du texte
            orientation='h'  # Barres horizontales
        )
    ])

    # Mise à jour du layout du graphique
    fig_bar.update_layout(
        barmode='stack',  # Les barres sont empilées par zone
        xaxis_title='Pourcentage de déplacements',  # Pourcentage sur l'axe x
        yaxis_title='Zone',  # Nom des zones sur l'axe y
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(title="Type de Volume"),
        margin=dict(l=50, r=50, t=100, b=50),
        yaxis=dict(autorange="reversed"),  # Inverser l'ordre des zones pour aligner avec l'image fournie
        xaxis=dict(range=[0, 100])  # Limite de l'axe x de 0 à 100 %
    )

    # Ajout du graphique aux composants
    components.append(dcc.Graph(id='deplacement-graph', figure=fig_bar, config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['toImage', 'zoom2d', 'pan2d'],
        'scrollZoom': False
    }))

    # Retourner le Div contenant le titre et le graphique
    return html.Div([
        html.Div([
            html.I(className='fas fa-chart-bar', style={'margin-right': '3rem', 'font-size': '1.5rem'}),
            html.H3("Pourcentage des Déplacements par Zone", style={'display': 'inline-block', 'textAlign': 'center', 'margin': 0},
                    id="title-Volume de Déplacements"),
            html.Span(
                html.I(className='fas fa-info-circle', style={'margin-left': '0.5rem', 'font-size': '1rem'}),
                id='info-icon-deplacement',  # ID correspondant pour le Popover
                style={'cursor': 'pointer'}
            ),
            # Ajout du Popover avec plus d'informations pour l'utilisateur amateur
            dbc.Popover(
                [
                    dbc.PopoverHeader("Détails sur la Visualisation - Pourcentage des Déplacements"),
                    dbc.PopoverBody([
                        "Ce graphique montre le pourcentage des déplacements produits et attirés par chaque zone. "
                        "Les 'Productions' indiquent la proportion de départs depuis une zone, tandis que les 'Attractions' représentent les arrivées dans cette zone.",
                        html.Br(), html.Br(),
                        html.B("Comment lire ce graphique :"),
                        html.Ul([
                            html.Li("Chaque barre représente une zone géographique, avec les déplacements mesurés en pourcentage."),
                            html.Li("Les barres bleues indiquent les 'Productions' (départs) en pourcentage."),
                            html.Li("Les barres oranges montrent les 'Attractions' (arrivées) en pourcentage."),
                            html.Li("En passant la souris sur chaque barre, vous pouvez voir le pourcentage exact de déplacements pour chaque zone.")
                        ]),
                        html.Br(),
                        "Ce graphique permet d'analyser la répartition des déplacements dans les différentes zones, offrant une vue d'ensemble des flux de mobilité.",
                        html.Br(), html.Br(),
                        html.I(className="fas fa-file-alt me-2"),
                        "Source de données : AGETIPA.",
                        html.Br(),
                        html.A("Cliquez ici pour plus de détails sur les données utilisées", href="https://www.exemple.com/details_deplacements", target="_blank", style={'color': '#007bff'})
                    ])
                ],
                id="popover-deplacement",  # ID unique pour le Popover
                target='info-icon-deplacement',  # Cible l'icône d'information
                trigger='hover',  # Affiche le popover au survol
                placement='right',
                style={'font-size': '0.8rem', 'max-width': '250px'}
            )
        ], className='custom-div'),
        *components
    ])


def generate_graph_vehicules(noms_zones=None):
    df_vehicules = get_nombre_vehicules_par_zone(noms_zones)

    components = []

    # Si une seule zone est sélectionnée, on crée un pie chart pour cette zone
    if noms_zones and len(noms_zones) == 1:
        zone_nom = noms_zones[0]
        zone_nom = zone_nom.lower()  # Transformation du nom de la zone en minuscule (ou majuscule si vous préférez)

        # Filtrer les données pour la zone sélectionnée
        df_zone = df_vehicules[df_vehicules['nom_commune'].str.lower() == zone_nom]
        df_zone = df_zone[df_zone['nombre_total'] > 0]  # Exclure les valeurs nulles ou égales à 0

        fig_pie = go.Figure(data=[
            go.Pie(
                labels=df_zone['type_vehicule'],
                values=df_zone['nombre_total'],
                textinfo='label+percent',
                insidetextorientation='radial'
            )
        ])

        fig_pie.update_layout(
            title=f"Répartition des types de véhicules dans la zone {zone_nom.capitalize()}",
            margin=dict(l=50, r=50, t=100, b=50)
        )

        components.append(dcc.Graph(id='vehicules-pie-chart', figure=fig_pie, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['toImage', 'zoom2d', 'pan2d'],
            'scrollZoom': False
        }))

    else:
        fig_bar = go.Figure()

        # Calculer les pourcentages pour chaque type de véhicule par zone
        df_totals = df_vehicules.groupby('nom_commune')['nombre_total'].sum().reset_index()
        df_totals.rename(columns={'nombre_total': 'total_vehicules'}, inplace=True)
        df_vehicules = df_vehicules.merge(df_totals, on='nom_commune')
        df_vehicules['pourcentage'] = df_vehicules['nombre_total'] / df_vehicules['total_vehicules'] * 100

        for type_vehicule in df_vehicules['type_vehicule'].unique():
            df_type = df_vehicules[df_vehicules['type_vehicule'] == type_vehicule]

            fig_bar.add_trace(go.Bar(
                name=type_vehicule,
                y=df_type['nom_commune'],  # Nom des zones sur l'axe y
                x=df_type['pourcentage'],  # Pourcentage sur l'axe x
                text=df_type['pourcentage'].round(2).astype(str) + '%',  # Ajout du texte en pourcentages sur les barres
                textposition='auto',  # Position automatique du texte
                orientation='h'  # Barres horizontales
            ))

        # Mise à jour du layout du bar chart empilé
        fig_bar.update_layout(
            barmode='stack',  # Empiler les barres
            title='Répartition des types de véhicules par zone (en %)',
            xaxis_title='Pourcentage de véhicules',
            yaxis_title='Zone',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(title="Type de Véhicule"),
            margin=dict(l=50, r=50, t=100, b=50),
            yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, 100])  # Plage de l'axe x de 0 à 100 %
        )

        components.append(dcc.Graph(id='vehicules-bar-chart', figure=fig_bar, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['toImage', 'zoom2d', 'pan2d'],
            'scrollZoom': False
        }))

    # Retourner le Div contenant le titre et le graphique
    return html.Div([
        html.Div([
            html.I(className='fas fa-chart-pie', style={'margin-right': '1rem', 'font-size': '1.5rem'}),
            html.H3("Répartition des Véhicules", style={'display': 'inline-block', 'textAlign': 'center', 'margin': 0},
                    id="title-Repartition-Vehicules"),
            html.Span(
                html.I(className='fas fa-info-circle', style={'margin-left': '0.5rem', 'font-size': '1rem'}),
                id='info-icon-repartition',  # ID correspondant pour le Popover
                style={'cursor': 'pointer'}
            ),
            # Ajout du Popover avec plus de détails pour le contexte et les explications
            dbc.Popover(
                [
                    dbc.PopoverHeader("Détails sur la Visualisation - Répartition des Véhicules"),
                    dbc.PopoverBody([
                        "Cette visualisation montre la répartition des types de véhicules par zone géographique.",
                        html.Br(), html.Br(),
                        html.B("Comment lire ce graphique :"),
                        html.Ul([
                            html.Li("Si une seule zone est sélectionnée, la répartition des types de véhicules est affichée sous forme de diagramme circulaire (pie chart), montrant le pourcentage de chaque type de véhicule."),
                            html.Li("Si plusieurs zones sont sélectionnées, le graphique affiche un diagramme à barres empilées, indiquant la proportion de chaque type de véhicule pour chaque zone."),
                            html.Li("Les couleurs différencient les types de véhicules pour faciliter la comparaison visuelle."),
                            html.Li("Le pourcentage sur l'axe x représente la part relative de chaque type de véhicule dans la zone ou les zones sélectionnées.")
                        ]),
                        html.Br(),
                        "Ce graphique permet d'identifier quels types de véhicules prédominent dans chaque zone et d'obtenir une vue d'ensemble de la répartition des modes de transport.",
                        html.Br(), html.Br(),
                        html.I(className="fas fa-file-alt me-2"),
                        "Source de données : AGETIPA.",
                        html.Br(),
                        html.A("Cliquez ici pour plus de détails sur les données utilisées", href="https://www.exemple.com/details_vehicules", target="_blank", style={'color': '#007bff'})
                    ])
                ],
                id="popover-repartition",  # ID unique pour le Popover
                target='info-icon-repartition',  # Cible l'icône d'information
                trigger='hover',  # Affiche le popover au survol
                placement='right',
                style={'font-size': '0.8rem', 'max-width': '250px'}
            )
        ], className='custom-div'),
        *components
    ])

def generate_sankey_diagram(noms_zones=None):
    df_matrice = get_od_count(noms_zones)

    # Créer une liste unique des zones pour les nœuds
    zones = list(pd.concat([df_matrice['nom_origine'], df_matrice['nom_destination']]).unique())

    # Créer des indices pour les zones
    zone_indices = {zone: i for i, zone in enumerate(zones)}

    sources = [zone_indices[zone] for zone in df_matrice['nom_origine']]
    targets = [zone_indices[zone] for zone in df_matrice['nom_destination']]
    values = df_matrice['nombre_deplacements']

    # Créer les couleurs pour les nœuds
    node_colors = ['#1f77b4' if i < len(df_matrice['nom_origine'].unique()) else '#ff7f0e' for i in range(len(zones))]

    # Créer le diagramme de Sankey avec deux colonnes
    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=zones,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=[f"rgba(31, 119, 180, {value/sum(values):.2f})" for value in values]  # Assigner des couleurs avec opacité variable selon la valeur
        )
    ))

    fig_sankey.update_layout(
        title_text="Flux de Déplacements entre Zones",
        font_size=10
    )

    # Retourner le Div contenant le titre et le graphique
    return html.Div([
        html.Div([
            html.I(className='fas fa-chart-line', style={'margin-right': '3rem', 'font-size': '1.5rem'}),
            html.H3("Flux de Déplacements entre Zones", style={'display': 'inline-block', 'textAlign': 'center', 'margin': 0},
                    id="title-Flux-Deplacements"),
            html.Span(
                html.I(className='fas fa-info-circle', style={'margin-left': '0.5rem', 'font-size': '1rem'}),
                id='info-icon-matrice',  # ID correspondant pour le Popover
                style={'cursor': 'pointer'}
            ),
            # Ajout du Popover avec plus d'informations pour l'utilisateur amateur
            dbc.Popover(
                [
                    dbc.PopoverHeader("Détails sur la Visualisation - Diagramme de Sankey"),
                    dbc.PopoverBody([
                        "Ce diagramme de Sankey montre les flux de déplacements entre différentes zones urbaines. "
                        "Il représente les zones d'origine (à gauche) et de destination (à droite), avec des liens reliant chaque zone pour illustrer le nombre de déplacements entre elles.",
                        html.Br(), html.Br(),
                        html.B("Comment lire ce graphique :"),
                        html.Ul([
                            html.Li("Chaque bloc représente une zone géographique."),
                            html.Li("La largeur des liens entre les zones est proportionnelle au nombre de déplacements : plus le lien est large, plus le flux est important."),
                            html.Li("Les couleurs permettent de distinguer les zones d'origine et de destination pour une meilleure compréhension des flux."),
                            html.Li("En passant la souris sur un lien, vous pouvez voir le nombre exact de déplacements entre deux zones.")
                        ]),
                        html.Br(),
                        "Cette visualisation aide à comprendre les principaux corridors de mobilité et les zones les plus connectées.",
                        html.Br(), html.Br(),
                        html.I(className="fas fa-file-alt me-2"),
                        "Source de données : AGETIPA.",
                        html.Br(),
                        html.A("Cliquez ici pour plus de détails sur les données utilisées", href="https://www.exemple.com/details_sankey", target="_blank", style={'color': '#007bff'})
                    ])
                ],
                id="popover-matrice",  # ID unique pour le Popover
                target='info-icon-matrice',  # Cible l'icône d'information
                trigger='hover',  # Affiche le popover au survol
                placement='right',
                style={'font-size': '0.8rem', 'max-width': '250px'}
            )
        ], className='custom-div'),
        dcc.Graph(id='sankey-diagram', figure=fig_sankey, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['toImage', 'zoom2d', 'pan2d'],
            'scrollZoom': False
        })
    ])

