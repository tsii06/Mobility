from dash import dcc, html
import dash_bootstrap_components as dbc

from src.data.scenario_data_process import fetch_scenarios_from_db


def get_scenario_options():
    df = fetch_scenarios_from_db()
    return [{'label': row['nom_scenario'], 'value': row['id_scenario']} for index, row in df.iterrows()]

# Fonction pour générer un KPI
def generate_kpi_card(value, label, color):
    return dbc.Card(
        dbc.CardBody([
            html.H4(f"{value}", className="card-title text-center"),
            html.P(label, className="text-center")
        ]),
        style={"background-color": color, "width": "100%", "border-radius": "10px"}
    )

# Fonction pour générer les KPI pour un scénario
def generate_scenario_kpi(scenario_data):
    return dbc.Row([
        dbc.Col(generate_kpi_card(scenario_data['vitesse_moyenne'], "Vitesse", "#e6f5ff" if scenario_data['vitesse_moyenne'] > 0 else "#ffcccc"), width=2),
        dbc.Col(generate_kpi_card(scenario_data['debit_moyen'], "Débit", "#e6f5ff" if scenario_data['debit_moyen'] > 0 else "#ffcccc"), width=2),
        dbc.Col(generate_kpi_card(scenario_data['temps_trajet_moyen'], "Temps Trajet", "#e6f5ff" if scenario_data['temps_trajet_moyen'] > 0 else "#ffcccc"), width=2),
        dbc.Col(generate_kpi_card(scenario_data['CO2'], "CO2", "#e6f5ff" if scenario_data['CO2'] > 0 else "#ffcccc"), width=2),
        dbc.Col(generate_kpi_card(scenario_data['NOx'], "NOx", "#e6f5ff" if scenario_data['NOx'] > 0 else "#ffcccc"), width=2)
    ])

# Fonction pour générer une comparaison de scénarios depuis la base de données
def generate_comparison_list(selected_scenarios):
    df = fetch_scenarios_from_db()  # Assurez-vous que cette fonction récupère les bons scénarios
    df_selected = df[df['id_scenario'].isin(selected_scenarios)]

    comparison_list = []

    # Comparaison de chaque scénario avec tous les autres
    for i, row1 in df_selected.iterrows():
        for j, row2 in df_selected.iterrows():
            if row1['id_scenario'] != row2['id_scenario']:  # Ne pas comparer un scénario avec lui-même
                comparison_list.append({
                    'Scénario 1': row1['nom_scenario'],
                    'Scénario 2': row2['nom_scenario'],
                    'Différence Vitesse': row1['vitesse_moyenne'] - row2['vitesse_moyenne'],
                    'Vitesse Référence': row1['vitesse_moyenne'],
                    'Vitesse Comparée': row2['vitesse_moyenne'],
                    'Différence Débit': row1['debit_moyen'] - row2['debit_moyen'],
                    'Débit Référence': row1['debit_moyen'],
                    'Débit Comparée': row2['debit_moyen'],
                    'Différence Temps de Trajet': row1['temps_trajet_moyen'] - row2['temps_trajet_moyen'],
                    'Temps Référence': row1['temps_trajet_moyen'],
                    'Temps Comparée': row2['temps_trajet_moyen'],
                    'Différence Volume Carburant': row1['volume_carburant_simule'] - row2['volume_carburant_simule'],
                    'Carburant Référence': row1['volume_carburant_simule'],
                    'Carburant Comparée': row2['volume_carburant_simule'],
                    'Différence Longueur Trajet': row1['longueur_trajet_moyenne'] - row2['longueur_trajet_moyenne'],
                    'Longueur Référence': row1['longueur_trajet_moyenne'],
                    'Longueur Comparée': row2['longueur_trajet_moyenne'],
                    'Différence CO2': row1['co2'] - row2['co2'],
                    'CO2 Référence': row1['co2'],
                    'CO2 Comparée': row2['co2'],
                    'Différence NOx': row1['nox'] - row2['nox'],
                    'NOx Référence': row1['nox'],
                    'NOx Comparée': row2['nox'],
                    'Différence CO': row1['co'] - row2['co'],
                    'CO Référence': row1['co'],
                    'CO Comparée': row2['co']
                })

    return comparison_list



def create_category_section(title, indicators, bg_color=None):
    """Crée une section de comparaison avec des indicateurs, affichés en ligne horizontalement."""
    return html.Div([
        html.H6(title, className="category-title", style={'margin-bottom': '10px', 'font-weight': 'bold'}),
        html.Div([
            html.Div([
                html.I(className=icon, style={'margin-right': '5px'}),
                html.Span(f"{name}: "),
                # Ajout des valeurs avec parenthèses pour l'indicateur de référence et de comparaison
                html.Span(f"{diff_value} ({ref_value} -> {comp_value}) {unit}",
                          style={'color': 'green' if diff_value > 0 else 'red'})
            ], className="kpi-item",
                style={'display': 'flex', 'align-items': 'center', 'margin-right': '20px', 'width': '50%'})
            for name, (diff_value, ref_value, comp_value), unit, icon in indicators
        ], className="kpi-container", style={'display': 'flex', 'flex-direction': 'row', 'gap': '10px',
                                             'background-color': bg_color or 'transparent', 'padding': '10px',
                                             'border-radius': '5px'})
    ], className="comparison-category", style={'margin-bottom': '15px'})


# Générer les cartes d'impact pour chaque scénario avec disposition horizontale pour chaque comparaison
def generate_impact_card(selected_scenarios):
    comparison_list = generate_comparison_list(selected_scenarios)

    if not comparison_list:
        return dbc.Card(
            dbc.CardBody("Aucune comparaison disponible."),
            className="mb-3"
        )

    # Organisation des comparaisons par scénario principal
    scenario_grouped_comparisons = {}
    for comparison in comparison_list:
        scenario_1 = comparison['Scénario 1']
        if scenario_1 not in scenario_grouped_comparisons:
            scenario_grouped_comparisons[scenario_1] = []
        scenario_grouped_comparisons[scenario_1].append(comparison)

    # Générer une carte pour chaque scénario
    cards = []
    for scenario, comparisons in scenario_grouped_comparisons.items():
        card_content = []

        # Titre principal pour indiquer le scénario de référence
        card_content.append(html.H4(f"Scénario Référence : {scenario}", className="text-center",
                                    style={'color': '#006400', 'font-weight': 'bold', 'margin-bottom': '20px'}))

        # Liste des colonnes pour afficher les comparaisons horizontalement
        comparison_columns = []

        for index, comparison in enumerate(comparisons):
            # Définir une couleur de fond pour alterner les comparaisons
            bg_color = '#f9f9f9' if index % 2 == 0 else 'white'

            # Sous-titre pour chaque comparaison, indiquant le scénario comparé
            comparison_title = html.H6(
                f"Comparaison avec le Scénario : {comparison['Scénario 2']}",
                className="comparison-subtitle",
                style={'font-weight': 'bold', 'margin-top': '15px', 'color': '#333'}
            )

            # Sections d'indicateurs par catégories avec les valeurs de référence et de comparaison
            transport_performance = [
                ("Vitesse",
                 (comparison['Différence Vitesse'], comparison['Vitesse Référence'], comparison['Vitesse Comparée']),
                 "km/h", "fas fa-tachometer-alt"),
                ("Débit", (comparison['Différence Débit'], comparison['Débit Référence'], comparison['Débit Comparée']),
                 "véhicules/h", "fas fa-road"),
                ("Temps de Trajet", (
                comparison['Différence Temps de Trajet'], comparison['Temps Référence'], comparison['Temps Comparée']),
                 "min", "fas fa-clock"),
                ("Longueur Trajet", (comparison['Différence Longueur Trajet'], comparison['Longueur Référence'],
                                     comparison['Longueur Comparée']), "km", "fas fa-arrows-alt-h")
            ]

            fuel_consumption = [
                ("Volume Carburant", (comparison['Différence Volume Carburant'], comparison['Carburant Référence'],
                                      comparison['Carburant Comparée']), "L", "fas fa-gas-pump")
            ]

            emissions = [
                ("CO2", (comparison['Différence CO2'], comparison['CO2 Référence'], comparison['CO2 Comparée']), "g",
                 "fas fa-cloud"),
                ("NOx", (comparison['Différence NOx'], comparison['NOx Référence'], comparison['NOx Comparée']), "g",
                 "fas fa-smog"),
                ("CO", (comparison['Différence CO'], comparison['CO Référence'], comparison['CO Comparée']), "g",
                 "fas fa-wind")
            ]

            # Ajouter chaque comparaison dans une colonne
            comparison_columns.append(dbc.Col(
                html.Div([
                    comparison_title,
                    create_category_section("Performance de Transport", transport_performance, bg_color),
                    create_category_section("Consommation de Carburant", fuel_consumption, bg_color),
                    create_category_section("Émissions de Gaz", emissions, bg_color)
                ], style={'padding': '15px', 'border': f'1px solid #ddd', 'border-radius': '8px',
                          'background-color': bg_color}),
                width=12  # Largeur pour chaque colonne (réparties horizontalement)
            ))

        # Ajouter une ligne avec toutes les colonnes de comparaison horizontalement
        card_content.append(dbc.Row(comparison_columns, style={'margin-top': '20px'}))

        # Créer la carte pour le scénario avec toutes les comparaisons
        cards.append(dbc.Card(
            dbc.CardBody([
                *card_content
            ]),
            className="mb-3"
        ))

    return html.Div(cards)
def generate_card_header_with_tooltip(title, table_id):
    return html.Div([
        html.Span(title),
        html.I(className="fas fa-info-circle", id=f"info-{table_id}", style={'cursor': 'pointer', 'margin-left': '20px'}),
        dbc.Tooltip("Les données affichées ici sont extraites des simulations SUMO", target=f"info-{table_id}", placement="top")
    ], style={'display': 'inline-flex', 'align-items': 'center'})


def generate_table(row_headers, scenario_ids, table_id):
    dataframe = fetch_scenarios_from_db()

    # Utilisation des noms de scénarios pour les en-têtes de colonnes
    table_header = [html.Thead(
        html.Tr(
            [html.Th("Indicateurs")] + [html.Th(dataframe.loc[dataframe['id_scenario'] == sc, 'nom_scenario'].values[0])
                                        for sc in scenario_ids])
    )]

    table_body = []
    for row_header in row_headers:
        # Extraire les valeurs de chaque scénario pour l'indicateur actuel
        row_values = [
            dataframe.loc[dataframe['id_scenario'] == sc, row_header].values[0]
            for sc in scenario_ids
        ]
        max_value = max(row_values)  # Trouver la valeur maximale dans la ligne

        # Construire chaque ligne du tableau
        row = [html.Td(row_header)]  # Première cellule de la ligne : l'indicateur (nom de la ligne)
        for value in row_values:
            # Appliquer une couleur au texte si la valeur est la valeur maximale de la ligne
            if value == max_value:
                row.append(html.Td(value, style={'color': 'red', 'font-weight': 'bold'}))
            else:
                row.append(html.Td(value))

        table_body.append(html.Tr(row))

    return dbc.Table(
        table_header + [html.Tbody(table_body)],
        bordered=True,
        hover=True,
        responsive=True,
        id=table_id
    )
