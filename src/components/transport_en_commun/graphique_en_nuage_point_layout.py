from dash import html, dcc
import dash_bootstrap_components as dbc


def graphique_en_nuage_point():
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Sélectionner les indicateurs", className="mb-2"),
                    # Dropdown pour l'axe X
                    dcc.Dropdown(
                        id='indicateur-dropdown-x',
                        options=[
                            {'label': 'Nombre de passagers', 'value': 'nombre_passager_jour'},
                            {'label': 'Distance Primus-Terminus', 'value': 'distance_primus_terminus'},
                            {'label': 'Nombre de transport_en_commun', 'value': 'nombre_bus_jour'},
                            {'label': 'Nombre de rotation par jour', 'value': 'nombre_rotation'},
                            {'label': 'Consommation moyen par jour', 'value': 'consomation_jour'},
                        ],
                        value='nombre_passager_jour',
                        className="mb-2",
                        placeholder="Sélectionner l'indicateur pour l'axe X"
                    ),
                    # Dropdown pour l'axe Y
                    dcc.Dropdown(
                        id='indicateur-dropdown-y',
                        options=[
                            {'label': 'Nombre de passagers', 'value': 'nombre_passager_jour'},
                            {'label': 'Distance Primus-Terminus', 'value': 'distance_primus_terminus'},
                            {'label': 'Nombre de transport_en_commun', 'value': 'nombre_bus_jour'},
                            {'label': 'Nombre de rotation par jour', 'value': 'nombre_rotation'},
                            {'label': 'Consommation moyen par jour', 'value': 'consomation_jour'},
                        ],
                        value='nombre_bus_jour',
                        className="mb-2",
                        placeholder="Sélectionner l'indicateur pour l'axe Y"
                    ),



                ], width=4, className="sidebar p-5", style={
                    "background-color": "#f8f9fa",
                    "border-radius": "8px",
                    "overflow-y": "auto"
                }),

                # Colonne pour le graphique avec statistiques et titre dynamique
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H5("Graphique de l'indicateur sélectionné", className="text-center"),
                            style={"background-color": "rgba(0, 147, 69, 0.43)", "border-radius": "5px"}
                        ),
                        dbc.CardBody([
                            # Graphique
                            dcc.Graph(id='scatter'),
                            # Indicateurs de corrélation et moyenne/médiane
                            html.Div(id="statistiques", className="mt-3")
                        ])
                    ])
                ], width=8)
            ])
        ]
    )
