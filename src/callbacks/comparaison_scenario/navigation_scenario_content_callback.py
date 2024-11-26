from dash.dependencies import Input, Output, State
import dash
from dash import html

from src.components.comparaison_scenario.comparaison_scenario_layout import comparaison
from src.components.comparaison_scenario.create_scenario import simulation


def navigation_scenarion_content_callback(app):
    @app.callback(
        Output('dynamic-content-comparaison_scenario', 'children'),
        [Input('simulation', 'n_clicks'),
         Input('comparaison', 'n_clicks')]
    )
    def update_content(simulation_clicks, comparaison_clicks):
        ctx = dash.callback_context

        if not ctx.triggered:
            return simulation()

        # Obtenir l'ID du bouton cliqué
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'simulation':
            # Contenu pour l'onglet 'SIMULATION'
            return simulation()
        elif button_id == 'comparaison':
            # Contenu pour l'onglet 'COMPARAISON'
            return comparaison()

        # Si aucun bouton n'a été cliqué (devrait être impossible avec cette configuration)
        return html.P("Sélectionnez une option.")
