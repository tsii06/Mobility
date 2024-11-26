from dash import html
import dash_bootstrap_components as dbc

def accueil():
    # Contenu structuré pour la page d'tableau_de_bord
    content = dbc.Container(
        children=[
            # Titre principal
            dbc.Row(
                dbc.Col(
                    html.H1("Visualisation de la mobilité à Antananarivo", className="text-center text-primary mb-4"),
                    width=12
                )
            ),
            # Introduction
            dbc.Row(
                dbc.Col(
                    html.P(
                        "Cette plateforme a été développée par l'AGETIPA pour analyser, visualiser et comparer les données "
                        "de mobilité urbaine d'Antananarivo. Elle vise à fournir des outils interactifs pour soutenir la "
                        "prise de décision des urbanistes et des décideurs.",
                        className="text-center"
                    ),
                    width=12
                )
            ),
            # Indicateurs clés
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("59 Lignes de Bus", className="card-title"),
                                html.P("Réseau de transport en commun desservant les zones clés d'Antananarivo."),
                            ]),
                            className="shadow-sm"
                        ),
                        width=4
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("230 000+ Habitants", className="card-title"),
                                html.P("Population estimée dans le 1er arrondissement d'Antananarivo."),
                            ]),
                            className="shadow-sm"
                        ),
                        width=4
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("10+ Indicateurs", className="card-title"),
                                html.P("Analyse des flux, densité de population, et plus encore."),
                            ]),
                            className="shadow-sm"
                        ),
                        width=4
                    ),
                ],
                className="mb-4"
            ),

            # Note ou rappel
            dbc.Row(
                dbc.Col(
                    html.P(
                        "Pour toute question ou suggestion, contactez l'équipe de l'AGETIPA.",
                        className="text-center text-muted mt-4"
                    ),
                    width=12
                )
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Contacts", className="card-title text-center", style={"color": "#3da870"}),
                            html.P([
                                "Email : ",
                                html.A("agetipa@gmail.com", href="mailto:agetipa@gmail.com", className="text-info"),
                                html.Br(),
                                "Téléphone : + 261 20 76 336 12 - 76 206 96 - 76 330 84 ",
                                html.Br(),
                                "Adresse :  Immeuble Le Colisée - 2ème étage LOT II W 26 X Ampasanimalo- ANTANANARIVO 101."
                            ], className="text-center")
                        ]),
                        className="mb-4 shadow-sm"
                    ),
                    width=12
                )
            ),
        ],
        style={
            'padding': '20px',
            'background-color': '#f9f9f9',
            'border-radius': '5px',
            'box-shadow': '0px 4px 6px rgba(0,0,0,0.1)',
            'margin-top': '40px'
        }
    )
    return content
