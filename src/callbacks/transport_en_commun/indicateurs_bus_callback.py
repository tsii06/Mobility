from dash import dcc
from dash import Output, Input,html

from src.data.bus_line_data_process import  get_all_ligne_from_database, enrich_lignes_data
from src.data.utils import create_excel
from src.components.transport_en_commun.bus_carte_element import generate_graphique_en_barre, generate_graphique_en_nuage_point
import dash_bootstrap_components as dbc

# df = extractKodatuDataBus()
df_lignes = get_all_ligne_from_database()
df = enrich_lignes_data()
finance_columns = [
    'numero_ligne', 'cout_carburant_par_jour', 'revenu_par_jour',
    'cout_exploitation_total',
    'rentabilite_par_jour', 'cout_par_passager'
]

resource_columns = [
    'numero_ligne', 'consomation_jour', 'nombre_bus_jour',
    'nombre_rotation', 'bus_par_km', 'distance_par_arret',
    'duree_rotation'
]

passenger_columns = [
    'numero_ligne', 'nombre_passager_jour', 'ratio_remplissage',
    'capacite_bus'
]

column_labels = {
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

def indicateurs_bus_callback(app):
    @app.callback(
        [Output('graphique', 'figure'),
         Output('kpi-moyenne', 'children'),
         Output('kpi-mediane', 'children'),
         Output('kpi-min', 'children'),
         Output('kpi-max', 'children')],
        [Input('indicateur-dropdown', 'value')]
    )
    def update_graph(indicateur):
        # Générer le graphique en fonction de l'indicateur sélectionné
        fig = generate_graphique_en_barre(df_lignes, indicateur)

        # Calcul des KPI (moyenne, médiane, minimum, maximum)
        moyenne = df_lignes[indicateur].mean()
        mediane = df_lignes[indicateur].median()
        valeur_min = df_lignes[indicateur].min()
        valeur_max = df_lignes[indicateur].max()

        # Retourner le graphique et les KPI séparément
        return fig, f"{moyenne:.2f}", f"{mediane:.2f}", f"{valeur_min:.2f}", f"{valeur_max:.2f}"

    @app.callback(
        Output('scatter', 'figure'),
        [Input('indicateur-dropdown-x', 'value'),
         Input('indicateur-dropdown-y', 'value')]
    )
    def update_graph(indicateur_x, indicateur_y):
        # Simule les données réelles ici
        return generate_graphique_en_nuage_point(df_lignes, indicateur_x, indicateur_y)



    @app.callback(
        Output('transport_en_commun-details-container', 'children'),
        Input('transport_en_commun-line-analyse_par_commune', 'value')
    )
    def update_bus_details(selected_lines):
        if not selected_lines:
            return []  # Retourne un contenu vide si aucune ligne n'est sélectionnée
        print(selected_lines)

        # Convertir en chaînes pour éviter les erreurs de type
        df_lignes['numero_ligne'] = df_lignes['numero_ligne'].astype(str)
        selected_lines = [str(line) for line in selected_lines]

        # Filtrer les données en fonction des lignes sélectionnées
        selected_data = df_lignes[df_lignes['numero_ligne'].isin(selected_lines)]
        print(selected_data)

        # Créer les lignes du tableau
        table_rows = []
        for _, row in selected_data.iterrows():
            table_rows.append(
                html.Tr([
                    html.Td(row['numero_ligne']),
                    html.Td(row['nombre_rotation']),
                    html.Td(row['nombre_vehicule']),
                    html.Td(row['nombre_passager_jour']),
                    html.Td(row['distance_aller_retour']),
                    html.Td(dcc.Link("Voir Détail", href=f"/detail_bus/{row['numero_ligne']}"))
                ])
            )

        # Créer le tableau Bootstrap
        table = dbc.Table(
            # En-têtes du tableau
            [html.Thead(html.Tr([
                html.Th("Ligne de transport_en_commun"),
                html.Th("Nombre de rotations"),
                html.Th("Nombre de transport_en_commun"),
                html.Th("Nombre de passagers par jour"),
                html.Th("Distance Aller-retour (km)"),
                html.Th("Détail")
            ]))] +
            # Corps du tableau
            [html.Tbody(table_rows)],
            bordered=True,
            striped=True,
            hover=True,
            responsive=True,
            className="mt-3"
        )

        # Retourne le tableau encapsulé dans un div
        return html.Div([table], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'})

    # Callback pour mettre à jour les données du tableau en fonction de la page actuelle
    @app.callback(
        [Output("finance-table-body", "children"),
         Output("resources-table-body", "children"),
         Output("passenger-table-body", "children")],
        [Input("finance-page", "data"),
         Input("resources-page", "data"),
         Input("passenger-page", "data")]
    )
    def update_tables(finance_page, resources_page, passenger_page):
        def format_num(value, unit=""):
            if isinstance(value, (float, int)):
                return f"{value:,.2f} {unit}".replace(",", " ").replace(".00", "")
            return value

        units = {
            'cout_carburant_par_jour': 'Ar',
            'revenu_par_jour': 'Ar',
            'cout_exploitation_total': 'Ar',
            'rentabilite_par_jour': 'Ar',
            'cout_par_passager': 'Ar',
            'consomation_jour': 'L',
            'nombre_bus_jour': 'transport_en_commun',
            'nombre_rotation': 'rot.',
            'bus_par_km': 'transport_en_commun/km',
            'distance_par_arret': 'km',
            'duree_rotation': 'min',
            'nombre_passager_jour': 'pass.',
            'ratio_remplissage': '%',
            'capacite_bus': 'places'
        }

        # Format des lignes pour chaque page et libellés naturels
        df_finance = df[['cout_carburant_par_jour', 'revenu_par_jour',
                         'cout_exploitation_total', 'rentabilite_par_jour', 'cout_par_passager']].iloc[
                     finance_page * 10:(finance_page + 1) * 10]
        df_resources = df[['consomation_jour', 'nombre_bus_jour', 'nombre_rotation', 'bus_par_km',
                           'distance_par_arret', 'duree_rotation']].iloc[resources_page * 10:(resources_page + 1) * 10]
        df_passenger = df[['nombre_passager_jour', 'ratio_remplissage', 'capacite_bus']].iloc[
                       passenger_page * 10:(passenger_page + 1) * 10]

        # Ajouter un numéro de ligne
        df_finance.insert(0, 'Numéro de ligne', range(finance_page * 10 + 1, (finance_page + 1) * 10 + 1))
        df_resources.insert(0, 'Numéro de ligne', range(resources_page * 10 + 1, (resources_page + 1) * 10 + 1))
        df_passenger.insert(0, 'Numéro de ligne', range(passenger_page * 10 + 1, (passenger_page + 1) * 10 + 1))

        # Appliquer les libellés et format numérique avec unités
        df_finance = df_finance.rename(columns=column_labels).apply(
            lambda row: [format_num(value, units.get(col, "")) for value, col in zip(row, df_finance.columns)], axis=1
        )
        df_resources = df_resources.rename(columns=column_labels).apply(
            lambda row: [format_num(value, units.get(col, "")) for value, col in zip(row, df_resources.columns)], axis=1
        )
        df_passenger = df_passenger.rename(columns=column_labels).apply(
            lambda row: [format_num(value, units.get(col, "")) for value, col in zip(row, df_passenger.columns)], axis=1
        )

        # Génération du contenu de chaque ligne avec alignement à gauche
        finance_body = [html.Tr([html.Td(cell, style={'text-align': 'left'}) for cell in row]) for row in
                        df_finance.values]
        resources_body = [html.Tr([html.Td(cell, style={'text-align': 'left'}) for cell in row]) for row in
                          df_resources.values]
        passenger_body = [html.Tr([html.Td(cell, style={'text-align': 'left'}) for cell in row]) for row in
                          df_passenger.values]

        return finance_body, resources_body, passenger_body

    @app.callback(
        Output("download-Performance Financière et Rentabilité-excel", "data"),
        Input("download-Performance Financière et Rentabilité-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def download_finance_excel(n_clicks):
        return dcc.send_bytes(create_excel(df[finance_columns]), "performance_financiere.xlsx")

    # Callback pour le tableau des ressources
    @app.callback(
        Output("download-Utilisation des Ressources et Efficacité Opérationnelle-excel", "data"),
        Input("download-Utilisation des Ressources et Efficacité Opérationnelle-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def download_resources_excel(n_clicks):
        return dcc.send_bytes(create_excel(df[resource_columns]), "utilisation_ressources.xlsx")

    # Callback pour le tableau des passagers
    @app.callback(
        Output("download-Volume de Passagers et Occupation-excel", "data"),
        Input("download-Volume de Passagers et Occupation-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def download_passenger_excel(n_clicks):
        return dcc.send_bytes(create_excel(df[passenger_columns]), "volume_passagers.xlsx")

    # Définir les colonnes pour chaque catégorie
