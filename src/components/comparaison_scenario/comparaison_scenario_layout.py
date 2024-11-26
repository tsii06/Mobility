from dash import dcc, html
import dash_bootstrap_components as dbc

from src.components.comparaison_scenario.scenario_figure import get_scenario_options


def comparaison():
    return dbc.Container([

        # Ligne pour sélectionner un scénario
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Sélection des Scénarios", className="text-center"),
                        style={'backgroundColor': 'rgba(0, 147, 69, 0.43)'}  # Couleur de l'en-tête
                    ),
                    dbc.CardBody([
                        dbc.Label("Veuillez sélectionner les scénarios pour la comparaison :"),
                        dcc.Dropdown(
                            id='comparaison_scenario-dropdown',
                            options=get_scenario_options(),
                            multi=True,
                            placeholder="Sélectionnez plusieurs scénarios",
                            value=['sc1', 'sc2']
                        ),
                    ])
                ], className="mb-4")  # Espacement en bas pour la carte de sélection
            ], width=12),
        ], className="my-3"),

        # Section combinée pour la comparaison : indicateurs de transport et émissions de gaz dans une seule carte
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Comparaison des Indicateurs de Transport et des Émissions de Gaz",
                                className="text-center"),
                        style={'backgroundColor': 'rgba(0, 147, 69, 0.43)'}  # Couleur de l'en-tête principal
                    ),
                    dbc.CardBody([
                        dbc.Row([  # Ligne pour organiser les deux tableaux côte à côte

                            # Colonne de gauche pour les indicateurs de transport
                            dbc.Col([
                                dbc.CardHeader(
                                    html.H6("Indicateurs de Transport", className="text-center"),
                                    style={'backgroundColor': '#f0f0f0', 'font-weight': 'bold'}
                                ),
                                html.Div(id='tableau-transport')
                            ], width=6),

                            # Colonne de droite pour les émissions de gaz
                            dbc.Col([
                                dbc.CardHeader(
                                    html.H6("Émissions de Gaz", className="text-center"),
                                    style={'backgroundColor': '#f0f0f0', 'font-weight': 'bold'}
                                ),
                                html.Div(id='tableau-gaz')
                            ], width=6)
                        ])
                    ])
                ], className="mb-4 shadow-sm")  # Ombrage léger pour la carte combinée
            ], width=12)
        ], className="mb-4"),  # Marges en bas pour espacer la section

        # Section d'impact des différences entre les scénarios
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Impact des Différences entre les Scénarios", className="text-center"),
                        style={'backgroundColor': 'rgba(0, 147, 69, 0.43)'}  # Couleur de l'en-tête
                    ),
                    dbc.CardBody(
                        html.Div(id='impact-card')
                    )
                ], className="mb-4 shadow-sm")
            ], width=12)
        ], className="mb-4")

    ], fluid=True)
