from dash import html
import dash_bootstrap_components as dbc


def simulation():

    return dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Container([
                dbc.Row([
                    # Colonne pour les informations de base du Scénario
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader(html.H5("Informations de base du Scénario", className="text-primary")),
                            dbc.CardBody([
                                dbc.Label('Nom du Scénario'),
                                dbc.Input(id='nom', type='text', placeholder='Nom du Scénario', className='mb-3'),

                                dbc.Label('Description'),
                                dbc.Textarea(id='description', placeholder='Description du Scénario', className='mb-3',
                                             style={'min-height': '60px'}),

                                dbc.Label('Type de Scénario'),
                                dbc.Input(id='type-comparaison_scenario', type='text', placeholder='Type de Scénario',
                                          className='mb-3'),
                            ])
                        ], className='mb-4 shadow-sm'),
                        width=4
                    ),

                    # Colonne pour les Données SUMO
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader(html.H5("Données SUMO", className="text-success")),
                            dbc.CardBody([
                                dbc.Label('Débit moyen (veh/h)'),
                                dbc.Input(id='debit', type='number', placeholder='Débit moyen', className='mb-3'),

                                dbc.Label('Vitesse moyenne (km/h)'),
                                dbc.Input(id='vitesse-moyenne', type='number', placeholder='Vitesse moyenne',
                                          className='mb-3'),

                                dbc.Label('Temps de trajet moyen (min)'),
                                dbc.Input(id='temps-trajet', type='number', placeholder='Temps de trajet moyen',
                                          className='mb-3'),

                                dbc.Label('Volume de carburant simulé (L)'),
                                dbc.Input(id='volume-carburant', type='number',
                                          placeholder='Volume de carburant simulé', className='mb-3'),

                                dbc.Label('Longueur de trajet moyenne (km)'),
                                dbc.Input(id='longueur-trajet-moyenne', type='number',
                                          placeholder='Longueur de trajet moyenne', className='mb-3'),
                            ])
                        ], className='mb-4 shadow-sm'),
                        width=4
                    ),

                    # Colonne pour les Aspects Environnementaux
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader(html.H5("Aspects Environnementaux", className="text-warning")),
                            dbc.CardBody([
                                dbc.Label('Émissions de CO2 (g/km)'),
                                dbc.Input(id='co2', type='number', placeholder='Émissions de CO2', className='mb-3'),

                                dbc.Label('Émissions de NOx (g/km)'),
                                dbc.Input(id='nox', type='number', placeholder='Émissions de NOx', className='mb-3'),

                                dbc.Label('Monoxyde de carbone (CO) (g/km)'),
                                dbc.Input(id='co', type='number', placeholder='Monoxyde de carbone', className='mb-3'),
                            ])
                        ], className='mb-4 shadow-sm'),
                        width=4
                    ),
                ], className="mb-4"),

                # Bouton de soumission et message de sortie
                dbc.Row([
                    dbc.Col(
                        dbc.Button("Enregistrer", id="submit-button", color="primary", className="mt-2"),
                        width=2
                    ),
                    dbc.Col(
                        html.Div(id="output-message", className="mt-3"),
                        width=10
                    )
                ], justify="end")
            ]),

            html.Div(id="output-message"),

        ], width=12),
    ])
], fluid=True)