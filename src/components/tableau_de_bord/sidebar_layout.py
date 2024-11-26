from dash import html, dcc, Dash, Output, Input
import dash_bootstrap_components as dbc

def sidebar_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H3("Thèmes", style={'display': 'inline-block', 'verticalAlign': 'middle'}),
                ],
                style={
                    'textAlign': 'center',
                    'padding': '10px',
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'display': 'flex',
                    'alignItems': 'center',  # Centrage vertical
                    'justifyContent': 'center'  # Centrage horizontal
                }
            ),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Checklist(
                                id='checklist-route',
                                options=[
                                    {
                                        'label': html.Span([
                                            'Segments routières avec le plus grand traffic'
                                        ]),
                                        'value': 'segment'
                                    },
                                    {
                                        'label': html.Span([
                                            'Itinéraire le plus empruntés'
                                        ]),
                                        'value': 'itineraire'
                                    },
                                    {
                                        'label': html.Span([
                                            'Route le plus congestioné'
                                        ]),
                                        'value': 'congestion'
                                    },
                                    {
                                        'label': html.Span([
                                            'Point de congestion dans le ville'
                                        ]),
                                        'value': 'point'
                                    },
                                ],
                                className='dash-checklist',
                                style={'padding': '10px'},
                            ),
                        ],
                        title="Trafic et Circulation",
                    ),
                ],
                flush=True,
            ),
            # Économie et Revenu
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Checklist(
                                id='checklist-thematiques',

                                options=[
                                    {
                                        'label': html.Span([
                                            'Densite de population'
                                        ]),
                                        'value': 'densite'
                                    },
                                    {
                                        'label': html.Span([
                                            'Typologie modale'
                                        ]),
                                        'value': 'typologie'
                                    },
                                    {
                                        'label': html.Span([
                                            'Matrice OD'
                                        ]),
                                        'value': 'matrice'
                                    },
                                    {
                                        'label': html.Span([
                                            'Volume de deplacement'
                                        ]),
                                        'value': 'volumes'
                                    }


                                ],

                                className='dash-checklist',
                                style={'padding': '10px'},
                                value=['densite'],

                            ),
                        ],
                        title="Mobilité et Données Démographiques",
                    ),
                ],
                flush=True
            ),
        ],
        style={
            'height': '90vh',  # Ajustez la hauteur selon vos besoins
            'overflow-y': 'auto',  # Active le défilement vertical
            'backgroundColor': '#2c3e50',  # Couleur de fond du sidebar
            'color': 'white',  # Couleur du texte
        },
        className='scroll-style'
    )