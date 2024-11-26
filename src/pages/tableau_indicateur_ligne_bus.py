from dash import dcc, Dash, html
import dash_bootstrap_components as dbc
from src.components.transport_en_commun.outi_bus import generate_table_ligne_bus

def bus_outil(app: Dash):
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.A(
                        [html.I(className="fas fa-arrow-left me-2"), "Retour"],
                        href="/transport_en_commun",  # URL de la page d'tableau_de_bord
                        className="text-muted",
                        style={'text-decoration': 'none', 'font-size': '14px'}
                    )
                ]),
                width=12
            )
        ], className="mb-2"),

        dbc.Row([
            dbc.Col(
                generate_table_ligne_bus(),
                className="mb-2 p-0",
                xs=12, sm=12, md=12, lg=12, xl=12
            )
        ]),
    ], fluid=True)
