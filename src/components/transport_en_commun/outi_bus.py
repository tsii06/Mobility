from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from src.data.bus_line_data_process import enrich_lignes_data

# Dictionnaire pour mapper les noms de colonnes vers des libellés plus lisibles
column_labels = {
    'numero_ligne': 'Numéro de ligne',
    'cout_carburant_par_jour': 'Coût de carburant par jour (Ar)',
    'revenu_par_jour': 'Revenu par jour (Ar)',
    'cout_exploitation_total': 'Coût total d\'exploitation (Ar)',
    'rentabilite_par_jour': 'Rentabilité par jour (Ar)',
    'cout_par_passager': 'Coût par passager (Ar)',
    'consomation_jour': 'Consommation moyenne par jour (L)',
    'nombre_bus_jour': 'Nombre de transport_en_commun par jour',
    'nombre_rotation': 'Nombre de rotations par jour',
    'bus_par_km': 'Bus par kilomètre',
    'distance_par_arret': 'Distance moyenne entre arrêts (km)',
    'duree_rotation': 'Durée moyenne d\'une rotation (min)',
    'nombre_passager_jour': 'Nombre de passagers par jour',
    'ratio_remplissage': 'Taux de remplissage moyen',
    'capacite_bus': 'Capacité d\'un transport_en_commun'
}


# Fonction de formatage des valeurs numériques avec unités et alignement
def format_value(value, column):
    units = {
        'Coût de carburant par jour (Ar)': 'Ar',
        'Revenu par jour (Ar)': 'Ar',
        'Coût total d\'exploitation (Ar)': 'Ar',
        'Rentabilité par jour (Ar)': 'Ar',
        'Coût par passager (Ar)': 'Ar',
        'Consommation moyenne par jour (L)': 'L',
        'Nombre de transport_en_commun par jour': '',
        'Nombre de rotations par jour': '',
        'Bus par kilomètre': 'transport_en_commun/km',
        'Distance moyenne entre arrêts (km)': 'km',
        'Durée moyenne d\'une rotation (min)': 'min',
        'Nombre de passagers par jour': 'passagers',
        'Taux de remplissage moyen': '%',
        'Capacité d\'un transport_en_commun': 'places'
    }
    unit = units.get(column, "")
    if isinstance(value, (float, int)):
        return f"{value:,.2f} {unit}".replace(",", " ").replace(".00", "")
    return value


# Fonction pour créer un tableau avec formatage et téléchargement
def create_table_ligne_bus(df, columns, title):
    # Appliquer le formatage aux données
    formatted_data = df[columns].copy()
    for col in columns:
        formatted_data[col] = formatted_data[col].apply(lambda x: format_value(x, col))

    return dbc.Card([
        dbc.CardHeader(html.H5(title, className="text-center")),
        dbc.CardBody([
            # Bouton de téléchargement
            html.Button("Télécharger Excel", id=f"download-{title}-btn", n_clicks=0, className="btn btn-primary mb-3"),
            dcc.Download(id=f"download-{title}-excel"),

            # Tableau avec pagination, tri et alignement des cellules à droite
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in columns],
                data=formatted_data.to_dict('records'),
                page_size=10,
                filter_action="native" if 'Numéro de ligne' in columns else None,
                sort_action="native",
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'right', 'padding': '5px'},  # Alignement à droite
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'textAlign': 'center'},
                editable=False
            )
        ])
    ], className="mb-4")


# Fonction principale pour afficher les tables par catégorie
def generate_table_ligne_bus():
    # Charger et renommer les données
    df = enrich_lignes_data().rename(columns=column_labels)

    # Colonnes pour chaque catégorie
    finance_columns = [
        'Numéro de ligne', 'Coût de carburant par jour (Ar)', 'Revenu par jour (Ar)',
        'Coût total d\'exploitation (Ar)', 'Rentabilité par jour (Ar)', 'Coût par passager (Ar)'
    ]
    resource_columns = [
        'Numéro de ligne', 'Consommation moyenne par jour (L)', 'Nombre de transport_en_commun par jour',
        'Nombre de rotations par jour', 'Bus par kilomètre', 'Distance moyenne entre arrêts (km)',
        'Durée moyenne d\'une rotation (min)'
    ]
    passenger_columns = [
        'Numéro de ligne', 'Nombre de passagers par jour', 'Taux de remplissage moyen', 'Capacité d\'un transport_en_commun'
    ]

    # Création de la disposition contenant les trois tables
    return html.Div([
        create_table_ligne_bus(df, finance_columns, "Performance Financière et Rentabilité"),
        create_table_ligne_bus(df, resource_columns, "Utilisation des Ressources et Efficacité Opérationnelle"),
        create_table_ligne_bus(df, passenger_columns, "Volume de Passagers et Occupation")
    ])
