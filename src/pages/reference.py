from dash import html
import dash_bootstrap_components as dbc

def reference():
    # Contenu structuré pour correspondre à votre projet
    content = dbc.Container(
        children=[
            # Titre principal
            dbc.Row(
                dbc.Col(
                    html.H3("Références", className='mb-4 text-primary'),
                    width=12
                )
            ),
            # Section "Contenu et réalisation"
            dbc.Row(
                dbc.Col(
                    [
                        html.H4("Contenu et réalisation", style={"color": "#3da870"}),
                        html.P(
                            "Ce projet a été développé au sein de l'AGETIPA. Les conceptions et les solutions proposées "
                            "sont issues d'observations et d'analyses réalisées par les membres de l'équipe d'AGETIPA. "
                            "L'objectif est de fournir une plateforme interactive pour analyser, visualiser et comparer "
                            "les données de trafic, de transport en commun et de démographie, en répondant aux besoins spécifiques "
                            "de la ville d'Antananarivo."
                        )
                    ],
                    width=12
                )
            ),
            # Section "Développement technique"
            dbc.Row(
                dbc.Col(
                    [
                        html.H4("Développement technique", style={"color": "#3da870"}),
                        html.P(
                            "Système de gestion : ReactJS / Python Flask / Plotly Dash / PostgreSQL / PostGIS. "
                            "Les données sont intégrées et visualisées via des cartes interactives en GeoJSON et des graphiques analytiques. "

                        ),
                        html.A(
                            "Le code source du projet est disponible sur GitHub : Lien vers le code",
                            href="https://github.com/votre-repo",
                            target="_blank",
                            className="text-info"
                        )
                    ],
                    width=12
                )
            ),

            # Section "Contacts"
            dbc.Row(
                dbc.Col(
                    [
                        html.H4("Contacts", style={"color": "#3da870"}),
                        html.P([
                            "Pour toute question ou demande d'information, veuillez contacter :",
                            html.Br(),
                            "Email : ", html.A("contact@agetipa.mg", href="mailto:contact@agetipa.mg", className="text-info"),
                            html.Br(),
                            "Téléphone : +261 20 22 123 45",
                            html.Br(),
                            "Adresse : AGETIPA, Rue XYZ, Antananarivo, Madagascar."
                        ])
                    ],
                    width=12
                )
            )
        ],
        style={
            'padding': '20px',
            'background-color': '#fff',
            'border': '1px solid #ddd',
            'border-radius': '5px',
            'margin-top': '20px',
            'box-shadow': '0px 4px 6px rgba(0,0,0,0.1)'
        }
    )

    return content
