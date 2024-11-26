from datetime import date
from dash.dependencies import Input, Output, State

from src.components.comparaison_scenario.scenario_figure import *
from src.data.scenario_data_process import fetch_two_most_recent_scenarios, insert_scenario_data


def insertion_scenario_callback(app):

    # Callback pour mettre à jour les tableaux et descriptions
    @app.callback(
        Output('tableau-transport', 'children'),
        Output('tableau-gaz', 'children'),
        Output('impact-card', 'children'),
        Input('comparaison_scenario-dropdown', 'value')
    )
    def update_content(selected_scenarios):
        # Si aucun scénario n'est sélectionné, charger les deux scénarios les plus récents
        if not selected_scenarios:
            try:
                recent_df = fetch_two_most_recent_scenarios()
                selected_scenarios = recent_df['id_scenario'].tolist()
            except Exception as e:
                return f"Erreur lors de la récupération des données : {e}", "", ""
        try:
            dataframe = fetch_scenarios_from_db()
            dataframe = dataframe[dataframe['id_scenario'].isin(selected_scenarios)]
        except Exception as e:
            return f"Erreur lors de la récupération des données : {e}", "", ""

        # Indicateurs de transport (vitesse, débit, temps de trajet, longueur)
        row_headers_transport = ['vitesse_moyenne', 'debit_moyen', 'temps_trajet_moyen', 'longueur_trajet_moyenne']
        table_transport = generate_table(row_headers_transport, selected_scenarios, "transport")

        # Emissions de gaz (CO2, CO, NOx)
        row_headers_gaz = ['co2', 'co', 'nox']
        table_gaz = generate_table( row_headers_gaz, selected_scenarios, "gaz")

        # Carte des impacts
        impact_card = generate_impact_card(selected_scenarios)

        return table_transport, table_gaz, impact_card

    # Callback pour insérer les données du formulaire dans la base de données
    @app.callback(
        Output("output-message", "children"),
        Input("submit-button", "n_clicks"),
        State("nom", "value"),
        State("description", "value"),
        State("type-comparaison_scenario", "value"),
        State("debit", "value"),
        State("vitesse-moyenne", "value"),
        State("temps-trajet", "value"),
        State("volume-carburant", "value"),
        State("longueur-trajet-moyenne", "value"),
        State("co2", "value"),
        State("nox", "value"),
        State("co", "value")
    )
    def submit_form(n_clicks, nom, description, type_scenario, debit, vitesse_moyenne, temps_trajet, volume_carburant,
                    longueur_trajet_moyenne, co2, nox, co):
        if n_clicks:
            try:
                # Appel à la fonction d'insertion dans la base de données
                insert_scenario_data(
                    nom=nom,
                    description=description,
                    type_scenario=type_scenario,
                    date_simulation=date.today(),
                    debit_moyen=debit,
                    vitesse_moyenne=vitesse_moyenne,
                    temps_trajet_moyen=temps_trajet,
                    volume_carburant_simule=volume_carburant,
                    longueur_trajet_moyenne=longueur_trajet_moyenne,
                    co2=co2,
                    nox=nox,
                    co=co
                )
                return "Données insérées avec succès."
            except Exception as e:
                return f"Erreur lors de l'insertion : {e}"
        return ""
