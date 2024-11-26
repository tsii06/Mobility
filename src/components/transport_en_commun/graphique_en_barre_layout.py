from dash import html, dcc, Dash, Output, Input
import dash_bootstrap_components as dbc

# Fonction pour créer un KPI simple avec un label et une valeur donnée
def create_kpi_card_simple(title, value_id, color):
    return html.Div([
        html.Span(title, style={"font-weight": "bold", "font-size": "16px", "color": color}),
        html.Span(id=value_id, style={"font-size": "16px", "margin-left": "10px"})
    ], style={
        "padding": "10px",
        "border": f"1px solid {color}",
        "border-radius": "8px",
        "margin-right": "10px",
        "text-align": "center",
        "background-color": "#f8f9fa"
    })

# Interface principale
def graphique_en_barre_layout():
    return html.Div([
        dbc.Row([
            # Colonne pour les filtres interactifs et le formulaire d'objectif
            dbc.Col([
                html.H4("Sélectionner les indicateurs", className="mb-3"),
                dcc.Dropdown(
                    id='indicateur-dropdown',
                    options=[
                        {'label': 'Nombre de passagers', 'value': 'nombre_passager_jour'},
                        {'label': 'Distance Primus-Terminus', 'value': 'distance_primus_terminus'},
                        {'label': 'Nombre de transport_en_commun', 'value': 'nombre_bus_jour'},
                        {'label': 'Nombre de rotation par jour', 'value': 'nombre_rotation'},
                    ],
                    value='nombre_passager_jour',
                    className="mb-4"
                ),

                # KPI alignés horizontalement
                html.Div([
                    create_kpi_card_simple("Moyenne", "kpi-moyenne", "#17a2b8"),
                    create_kpi_card_simple("Médiane", "kpi-mediane", "#28a745"),
                    create_kpi_card_simple("Valeur Min", "kpi-min", "#ffc107"),
                    create_kpi_card_simple("Valeur Max", "kpi-max", "#dc3545")
                ], style={
                    "display": "grid",
                    "grid-template-columns": "1fr 1fr",  # Deux colonnes
                    "gap": "10px",  # Espacement entre les cartes
                    "justify-items": "center"  # Centrer les cartes horizontalement
                }),

            ], width=4, className="sidebar p-4", style={
                "background-color": "#f8f9fa",
                "border-radius": "8px",
                "overflow-y": "auto",
                "padding": "20px"
            }),

            # Colonne pour le graphique
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Graphique de l'indicateur sélectionné", className="text-center"),
                        style={"background-color": "rgba(0, 147, 69, 0.43)", "border-radius": "5px"}
                    ),
                    dbc.CardBody(
                        dcc.Graph(id='graphique')
                    )
                ], className="shadow-sm")
            ], width=8)
        ], className="mb-4")
    ])
