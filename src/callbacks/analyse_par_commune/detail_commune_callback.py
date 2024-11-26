from dash import Output, Input, html
from src.data.commune_data_process import get_all_data_commune
import dash_bootstrap_components as dbc
from dash import dcc

def detail_commune_callback(app):
    @app.callback(
        Output('zone-detail-content', 'children'),
        Input('commune-dropdown', 'value')
    )
    def update_zone_details(selected_commune):
        # Obtenir les données pour la commune sélectionnée
        commune_data = get_all_data_commune(selected_commune)
        general_info = commune_data['general_info']
        age_distribution = commune_data['age_distribution']
        attraction_production = commune_data['attraction_production']
        connections = commune_data['connections']
        typologie_modale = commune_data['typologie_modale']

        return [
            # Lien pour retourner à l'tableau_de_bord
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.A([html.I(className="fas fa-arrow-left me-2"), "Retour à l'tableau_de_bord"], href="#",
                               className="text-muted", style={'text-decoration': 'none', 'font-size': '14px'})
                    ]),
                    width=12
                )
            ], className="mb-2"),

            # Vue d'ensemble de la population
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H5([html.I(className="fas fa-chart-bar me-2"), "Vue d'Ensemble"],
                                style={'font-weight': 'bold', 'margin-bottom': '15px'}),
                        html.H4(f"{general_info['population']:,}".replace(",", " "), className="text-primary", style={'font-weight': 'bold'}),
                        html.P(f"Cette zone représente environ {general_info['population_percentage']}% de la population totale d'Antananarivo.",
                               className="text-muted", style={'margin-bottom': '10px'}),
                        html.P(f"Elle se classe au {general_info['rank']}ème rang parmi les communes d'Antananarivo en termes de population.",
                               className="text-muted", style={'margin-bottom': '15px'}),
                        html.P([html.I(className="fas fa-file-alt me-2"),
                                "Source : INSTAT"],
                               className="text-muted small", style={'margin-top': '15px'})
                    ], style={'margin-right': '20px'}),
                    width=4
                ),

                # Graphique de répartition par tranche d'âge
                dbc.Col(
                    html.Div([
                        html.H5([html.I(className="fas fa-birthday-cake me-2"), "Répartition par Tranche d'Âge"],
                                style={'font-weight': 'bold', 'margin-bottom': '15px'}),
                        dcc.Graph(
                            figure={
                                'data': [
                                    {
                                        'y': list(age_distribution.keys()),
                                        'x': list(age_distribution.values()),
                                        'type': 'bar',
                                        'orientation': 'h',
                                        'marker': {'color': ['#ff6b6b', '#feca57', '#54a0ff', '#1dd1a1', '#5f27cd']}
                                    }
                                ],
                                'layout': {
                                    'title': '',
                                    'xaxis': {'title': 'Nombre de Population', 'showgrid': False, 'zeroline': False},
                                    'yaxis': {'title': 'Tranche d\'Âge'},
                                    'margin': {'l': 100, 'r': 50, 't': 20, 'b': 40},
                                    'height': 400,
                                }
                            },
                            config={'displayModeBar': False}
                        )
                    ]),
                    width=8
                )
            ], className="mb-5"),

            # Graphiques circulaires pour Attraction/Production et Typologie Modale
            dbc.Row([
                # Graphiques circulaires pour Attraction/Production et Typologie Modale
                dbc.Row([
                    # Graphique pour Attraction et Production
                    dbc.Col(
                        html.Div([
                            html.H5([html.I(className="fas fa-balance-scale me-2"), "Attraction et Production"],
                                    style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                            dcc.Graph(
                                figure={
                                    'data': [
                                        {
                                            'labels': ['Attraction', 'Production'],
                                            'values': [attraction_production['attraction'],
                                                       attraction_production['production']],
                                            'type': 'pie',
                                            'hole': .3,
                                            'marker': {'colors': ['#feca57', '#1dd1a1']}
                                        }
                                    ],
                                    'layout': {
                                        'title': '',
                                        'annotations': [
                                            {"font": {"size": 20}, "showarrow": False, "text": f"", "x": 0.5,
                                             "y": 0.5}],
                                        'height': 300,
                                        'margin': {'l': 20, 'r': 20, 't': 30, 'b': 30}
                                    }
                                },
                                config={'displayModeBar': False}
                            ),
                            html.P(
                                "Ce graphique montre la proportion entre l'attraction et la production dans la zone sélectionnée.",
                                className="text-muted", style={'font-size': '14px', 'margin-bottom': '15px'}),
                        ]),
                        width=6
                    ),

                    # Graphique pour la typologie modale
                    dbc.Col(
                        html.Div([
                            html.H5([html.I(className="fas fa-car-side me-2"), "Typologie Modale"],
                                    style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                            dcc.Graph(
                                figure={
                                    'data': [
                                        {
                                            'labels': ['Voiture', 'Moto', 'Bus'],
                                            'values': [typologie_modale['Voiture'], typologie_modale['Moto'],
                                                       typologie_modale['Bus']],
                                            'type': 'pie',
                                            'hole': .3,
                                            'marker': {'colors': ['#54a0ff', '#ff6b6b', '#5f27cd']}
                                        }
                                    ],
                                    'layout': {
                                        'title': '',
                                        'annotations': [
                                            {"font": {"size": 20}, "showarrow": False, "text": f"", "x": 0.5,
                                             "y": 0.5}],
                                        'height': 300,
                                        'margin': {'l': 20, 'r': 20, 't': 30, 'b': 30}
                                    }
                                },
                                config={'displayModeBar': False}
                            ),
                            html.P(
                                "Ce graphique montre la répartition des types de véhicules utilisés dans cette zone.",
                                className="text-muted", style={'font-size': '14px', 'margin-bottom': '15px'})
                        ]),
                        width=6
                    ),
                ], className="mb-5"),

                # Section pour les connexions aux autres zones
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.H6("Zones les plus connectées",
                                    style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                            dcc.Graph(
                                figure={
                                    'data': [
                                        {
                                            'y': connections['most_connected'],
                                            'x': connections['most_connected_counts'],
                                            'type': 'bar',
                                            'orientation': 'h',
                                            'marker': {'color': '#1dd1a1'}
                                        }
                                    ],
                                    'layout': {
                                        'title': '',
                                        'xaxis': {'title': 'Nombre de connexions', 'showgrid': False,
                                                  'zeroline': False},
                                        'yaxis': {'title': 'Zones'},
                                        'margin': {'l': 60, 'r': 20, 't': 10, 'b': 30},
                                        'height': 200
                                    }
                                },
                                config={'displayModeBar': False}
                            ),
                            html.P("Ce graphique montre les zones les plus connectées à la zone sélectionnée.",
                                   className="text-muted", style={'font-size': '14px', 'margin-top': '10px'})
                        ], style={'padding': '15px'}),
                        width=6
                    ),
                    dbc.Col(
                        html.Div([
                            html.H6("Zones les moins connectées",
                                    style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                            dcc.Graph(
                                figure={
                                    'data': [
                                        {
                                            'y': connections['least_connected'],
                                            'x': connections['least_connected_counts'],
                                            'type': 'bar',
                                            'orientation': 'h',
                                            'marker': {'color': '#ff6b6b'}
                                        }
                                    ],
                                    'layout': {
                                        'title': '',
                                        'xaxis': {'title': 'Nombre de connexions', 'showgrid': False,
                                                  'zeroline': False},
                                        'yaxis': {'title': 'Zones'},
                                        'margin': {'l': 60, 'r': 20, 't': 10, 'b': 30},
                                        'height': 200
                                    }
                                },
                                config={'displayModeBar': False}
                            ),
                            html.P("Ce graphique montre les zones les moins connectées à la zone sélectionnée.",
                                   className="text-muted", style={'font-size': '14px', 'margin-top': '10px'})
                        ], style={'padding': '15px'}),
                        width=6
                    ),
                ], className="mb-5")
            ])
        ]