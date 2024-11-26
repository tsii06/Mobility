from dash import dcc, html, Dash
import dash_bootstrap_components as dbc


def carte_ligne_bus_layout():
    return html.Div(
        children=[
            dcc.Store(id='selected-transport_en_commun-lines-store'),
            dcc.Store(id='legend-visible', data=False),  # Store to track legend visibility

            html.Div([

                html.Div([
                    dcc.Dropdown(
                        id='transport_en_commun-line-analyse_par_commune',
                        options=[],
                        multi=True,
                        placeholder="Sélectionnez une ou plusieurs lignes de transport_en_commun",
                        className="mb-4",
                        style={"width": "100%"}
                    )
                ], style={'flex': '1', 'marginRight': '10px'}),

                html.Div([
                    dcc.Store(id='selected-affichage', data=[]),
                    dbc.DropdownMenu(
                        label="Options de Visualisation",
                        children=[
                            dbc.Checklist(
                                options=[
                                    {'label': 'Repartition zonale', 'value': 'repartition'},
                                    {'label': 'Afficher les arrets de bus', 'value': 'stops'},
                                    {'label': 'Afficher les points de congestions', 'value': 'point'},
                                ],
                                id='transport_en_commun-visual-options',
                                inline=True,
                                className="mb-2"
                            )
                        ],
                        toggle_style={"width": "100%"},
                        className="mb-4",
                        right=False,
                    ),
                ], style={'flex': '1', 'marginRight': '10px'}),

                html.Div([
                    dcc.Dropdown(
                        id='ligne-visual-options',
                        options=[
                            {'label': 'Distance Aller-retour', 'value': 'nombre_rotation'},
                            {'label': 'Nombre de transport_en_commun', 'value': 'nombre_vehicule'},
                            {'label': 'Nombre de passager', 'value': 'nombre_passager_jour'}
                        ],
                        placeholder="Couleurs des lignes",
                        multi=False,
                        className="mb-4",
                        style={'width': '100%'}
                    )
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginLeft': '20px', 'marginTop': '10px'}),

            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id='transport_en_commun-map', style={'width': '100%', 'height': '80%'}),
                    html.Div(
                        id='couleur-legend',
                        style={
                            'position': 'absolute',
                            'top': '20px',
                            'right': '10px',
                            'background-color': 'rgba(255, 255, 255, 0.8)',
                            'padding': '10px',
                            'border-radius': '5px',
                            'z-index': '1000',
                            'display': 'flex',
                            'align-items': 'center',
                            'visibility': 'hidden'  # Start hidden
                        },
                        children=[
                            html.Span(id='left-speed', style={'color': '#1e90ff', 'margin-right': '10px'}),
                            html.Div(
                                style={
                                    'display': 'flex',
                                    'align-items': 'center',
                                    'gap': '5px',
                                },
                                children=[
                                    html.Div(style={'width': '20px', 'height': '10px', 'background-color': 'green'}),
                                    html.Div(style={'width': '20px', 'height': '10px', 'background-color': 'orange'}),
                                    html.Div(style={'width': '20px', 'height': '10px', 'background-color': 'red'}),
                                    html.Div(style={'width': '20px', 'height': '10px', 'background-color': 'black'}),
                                ]
                            ),
                            html.Span(id='right-speed', style={'color': '#1e90ff', 'margin-left': '10px'}),
                        ]
                    )
                ])
            ),
            html.Div(id='transport_en_commun-details-container'),
        ],
    )