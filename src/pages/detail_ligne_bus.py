from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from src.data.bus_line_data_process import enrich_lignes_data


# Fonction pour créer le KPI avec un icône d'infobulle
def get_kpi_layout(name, current_value, average_value, kpi_id):
    variation = ((current_value - average_value) * 100) / average_value if average_value != 0 else 0
    variation_text = f"{variation:.1f}%"
    arrow_color = "green" if variation > 0 else "red"
    arrow_icon = "↑" if variation > 0 else "↓"

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H6(name, className="card-title", style={"color": "#4a4a4a", "font-weight": "600"}),
                html.Span(
                    html.I(className='fas fa-info-circle', style={'margin-left': '0.5rem', 'font-size': '1rem'}),
                    id=f'info-icon-{kpi_id}', style={'cursor': 'pointer'}
                ),
                dbc.Tooltip(
                    f"Moyenne : {average_value:.2f}",
                    target=f'info-icon-{kpi_id}',
                    placement="top"
                )
            ], className="d-flex align-items-center justify-content-between"),
            html.H3(f"{current_value}", className="card-text", style={"font-weight": "bold", "color": "#2c3e50"}),
            html.Div([
                html.Span(f"{arrow_icon} {variation_text} ", style={"color": arrow_color, "font-weight": "bold"}),
                html.Span("par rapport à la moyenne", style={"color": "#888888"})
            ], style={"font-size": "small", "margin-top": "5px"})
        ])
    ], className="shadow-sm kpi-card", style={"height": "100%", "background-color": "#f8f9fa", "border-radius": "8px"})


# Fonction pour afficher les informations générales sur la ligne
def get_info_section(ligne_data):
    return dbc.Card([
        dbc.CardBody([
            html.H5("Information sur la Ligne", className="card-title",
                    style={"font-weight": "600", "color": "#2c3e50"}),
            html.P(f"Numéro de ligne : {ligne_data['numero_ligne']}", className="card-text"),
            html.P(f"Coopérative : {ligne_data['nom_cooperative']}", className="card-text"),
            html.P(f"Départ : {ligne_data['primus']}", className="card-text"),
            html.P(f"Arrivée : {ligne_data['terminus']}", className="card-text")
        ])
    ], className="shadow-sm", style={"height": "100%", "background-color": "#ffffff", "border-radius": "8px"})


# Fonction principale pour organiser les éléments


# Fonction principale pour organiser les éléments
# Fonction d'analyse textuelle basée sur les KPIs
def generate_analysis_text(ligne_data, capacite_totale_ligne, taux_occupation, average_benefit):
    # Analyse sur la rentabilité
    rentabilite = ligne_data['rentabilite_par_jour']
    if rentabilite < 0:
        rentabilite_text = (
            f"La ligne {ligne_data['numero_ligne']} n'est pas rentable, avec une rentabilité journalière de {rentabilite:.2f} Ar. "
            "Pour atteindre la rentabilité, il pourrait être nécessaire d’augmenter le nombre de passagers par jour, "
            "d'optimiser les coûts d'exploitation, ou de revoir les tarifs."
        )
    else:
        rentabilite_text = (
            f"La ligne {ligne_data['numero_ligne']} est rentable, avec une rentabilité journalière de {rentabilite:.2f} Ar. "
            "Cependant, il est recommandé de surveiller l’évolution de cette rentabilité pour maintenir un équilibre financier."
        )

    # Analyse sur le taux d'occupation
    if taux_occupation < 50:
        occupation_text = (
            f"Le taux d'occupation actuel de {taux_occupation:.1f}% est inférieur à 50%, ce qui indique une sous-utilisation des transport_en_commun. "
            "Envisagez de réduire le nombre de rotations ou d’ajuster les horaires pour optimiser l’utilisation des véhicules."
        )
    elif taux_occupation >= 80:
        occupation_text = (
            f"Le taux d'occupation de {taux_occupation:.1f}% est élevé, ce qui montre une bonne utilisation des transport_en_commun. "
            "Assurez-vous que les passagers continuent à bénéficier d’un confort adéquat pour maintenir ce niveau de remplissage."
        )
    else:
        occupation_text = (
            f"Le taux d'occupation de {taux_occupation:.1f}% est acceptable. "
            "Toutefois, des ajustements mineurs pourraient améliorer encore l’efficacité du remplissage."
        )

    # Analyse sur les coûts
    cout_par_rotation = ligne_data['cout_par_rotation']
    if cout_par_rotation > average_benefit * 0.2:
        cout_text = (
            f"Le coût par rotation est relativement élevé à {cout_par_rotation:.2f} Ar, représentant plus de 20% de la rentabilité moyenne. "
            "Réduire les coûts d'exploitation (par exemple, en optimisant la consommation de carburant ou en ajustant les rotations) "
            "peut aider à améliorer la rentabilité de la ligne."
        )
    else:
        cout_text = (
            f"Le coût par rotation de {cout_par_rotation:.2f} Ar est sous contrôle, contribuant positivement à la rentabilité de la ligne. "
            "Continuez à surveiller les coûts pour maintenir cette efficacité."
        )

    # Rassembler toutes les analyses en une seule chaîne de texte
    analysis_text = f"{rentabilite_text}\n\n{occupation_text}\n\n{cout_text}"
    return analysis_text




def ligne_detail(numero_ligne):
    df = enrich_lignes_data()  # Extraire les données enrichies

    numero_ligne = str(numero_ligne).strip()
    ligne_data_filtered = df[df['numero_ligne'].astype(str).str.strip() == numero_ligne]

    if ligne_data_filtered.empty:
        return dbc.Container(html.P(f"Aucune donnée trouvée pour le numéro de ligne {numero_ligne}",
                                    style={"color": "#d9534f", "font-size": "1.2em"}))

    ligne_data = ligne_data_filtered.iloc[0]
    capacite_par_bus = 27
    capacite_totale_ligne = ligne_data['nombre_bus_jour'] * capacite_par_bus * ligne_data['nombre_rotation'] * 2

    taux_occupation = (ligne_data['nombre_passager_jour'] / capacite_totale_ligne) * 100
    average_benefit = df['rentabilite_par_jour'].mean()

    # KPIs enrichis
    kpi_section = dbc.Row(
        [
            dbc.Col(get_kpi_layout("Distance (km)", round(ligne_data['distance_primus_terminus'], 2),
                                   df['distance_primus_terminus'].mean(), "distance"), width=4),
            dbc.Col(get_kpi_layout("Rentabilité (Ar)", round(ligne_data['rentabilite_par_jour'], 2),
                                   df['rentabilite_par_jour'].mean(), "rentabilite"), width=4),
            dbc.Col(get_kpi_layout("Taux d'occupation (%)", round(taux_occupation, 2), (
                        (df['nombre_passager_jour'] / (df['nombre_bus_jour'] * capacite_par_bus)) * 100).mean(),
                                   "occupation"), width=4),
            dbc.Col(get_kpi_layout("Coût par rotation (Ar)", round(ligne_data['cout_par_rotation'], 2),
                                   df['cout_par_rotation'].mean(), "cost_rotation"), width=4),
            dbc.Col(get_kpi_layout("Coût par passager (Ar)", round(ligne_data['cout_par_passager'], 2),
                                   df['cout_par_passager'].mean(), "cost_passenger"), width=4),
            dbc.Col(get_kpi_layout("Nombre de rotations", ligne_data['nombre_rotation'], df['nombre_rotation'].mean(),
                                   "rotations"), width=4)
        ],
        className="mb-4 g-4"
    )

    # Section d’analyse textuelle avec des observations
    analysis_text = generate_analysis_text(ligne_data, capacite_totale_ligne, taux_occupation, average_benefit)
    analysis_section = dbc.Card(
        dbc.CardBody([
            html.H6("Analyse et Recommandations", className="card-title",
                    style={"font-weight": "600", "color": "#2c3e50"}),
            html.P(analysis_text, style={"white-space": "pre-line", "font-size": "1em", "color": "#4a4a4a"})
        ]),
        className="shadow-sm", style={"background-color": "#ffffff", "border-radius": "8px"}
    )
    info_section = get_info_section(ligne_data)

    # Disposition finale pour une visualisation moderne
    layout = dbc.Container([
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
            dbc.Col(info_section, width=4),
            dbc.Col(kpi_section, width=8)
        ], className="mt-4"),

        # Ajouter la section d'analyse en dessous des KPIs
        dbc.Row([
            dbc.Col(analysis_section, width=12)
        ], className="mt-4")
    ], fluid=True, style={ "background-color": "#f5f5f5", "padding": "20px","margin": "20px", "border-radius": "8px","width": "95%"})

    return layout