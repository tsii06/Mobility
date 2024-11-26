from dash import html, dcc
import dash_bootstrap_components as dbc

def sidebar_bus():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.H4("Accédez à un outil de diagnostic détaillé", className="card-title"),
                html.P(
                    "Accédez aux outils détaillés pour diagnostiquer une ligne de transport_en_commun, "
                    "mettre en place des scénarios, et faire des comparaisons.",
                    className="card-text",
                ),

                dcc.Link(
                    dbc.Button("Plus d'outils", color="primary", className="mt-2"),
                    href="/outil_bus"  # Lien vers l'ancre cible
                )
            ]),
            style={"width": "80%", "margin": "auto", "text-align": "center"}
        ),
        html.Div([
            html.H5("Résumé sur les transport_en_commun à Antananarivo",
                    style={"text-align": "center", "margin-bottom": "10px", "color": "#333"}),
            html.P(
                [
                    "Antananarivo compte actuellement ",
                    html.Span("59", style={"font-weight": "bold"}),
                    " lignes de transport_en_commun en service. Le tarif actuel pour un trajet est de ",
                    html.Span("600 ariary", style={"font-weight": "bold"}),
                    ", couvrant plusieurs zones de la ville. Le réseau de transport_en_commun est un moyen de transport clé pour la population locale, desservant des zones résidentielles, commerciales et industrielles."
                ],
                style={"color": "#555", "line-height": "1.6"}
            ),
        ], style={
            "padding": "15px",
            # "background-color": "#f5f5f5",  # Couleur agréable à lire, légère sur fond gris
            "border-radius": "5px",
            "margin-bottom": "20px",
        }),

    ], className="sidebar p-3", style={

        "margin-top":"20px",
        "border-radius": "8px",
        "overflow-y": "auto"  # Permet le défilement vertical
    })
