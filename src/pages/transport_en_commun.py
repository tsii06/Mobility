import dash_bootstrap_components as dbc
from src.components.transport_en_commun.carte_ligne_bus_layout import carte_ligne_bus_layout
from src.components.transport_en_commun.graphique_en_barre_layout import graphique_en_barre_layout
from src.components.transport_en_commun.graphique_en_nuage_point_layout import graphique_en_nuage_point
from src.components.transport_en_commun.sidebar_bus import sidebar_bus


def bus():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                sidebar_bus(),
                xs=12, sm=12, md=4, lg=4, xl=4,  # Largeur pour différentes tailles d'écran
                className="mb-5 p-0",
                style={
                    "padding-top": "10px",
                    "background-color": "#f8f9fa",
                }
            ),
            dbc.Col(
                carte_ligne_bus_layout(),
                xs=12, sm=12, md=8, lg=8, xl=8,  # Largeur pour différentes tailles d'écran
                className="mb-5 p-0"
            ),
        ]),
        dbc.Row([
            dbc.Col(
                graphique_en_barre_layout(),
                className="mb-5 p-0",
                xs=12, sm=12, md=12, lg=12, xl=12
            )
        ]),

        dbc.Row([
            dbc.Col(
                graphique_en_nuage_point(),
                className="mb-2 p-0",
                xs=12, sm=12, md=12, lg=12, xl=12
            )
        ])
    ], fluid=True)
