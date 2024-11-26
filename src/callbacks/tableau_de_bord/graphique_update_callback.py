from dash.dependencies import Input, Output
from src.components.tableau_de_bord.graphique import generate_graph_deplacement, generate_graph_vehicules, \
    generate_sankey_diagram, generate_population_histogram
from dash import html
def graphique_update_callback(app):
    @app.callback(
        Output('densite', 'children'),
        [Input('selected-thematiques', 'data')]
    )
    def update_density_graph(selected_thematiques):
        # Vérifier si selected_thematiques n'est pas None
        if selected_thematiques and 'densite' in selected_thematiques:
            return generate_population_histogram()
        return html.Div()

    @app.callback(
        Output('typologie', 'children'),
        [Input('selected-thematiques', 'data'),
         Input('clicked-zones', 'data')]
    )
    def update_typology_graph(selected_thematiques, clicked_zones):
        # Vérifier si selected_thematiques et clicked_zones ne sont pas None
        if selected_thematiques and 'typologie' in selected_thematiques:
            return generate_graph_vehicules(noms_zones=clicked_zones)
        return html.Div()

    @app.callback(
        Output('matrice', 'children'),
        [Input('selected-thematiques', 'data'),
         Input('clicked-zones', 'data')]
    )
    def update_matrice_graph(selected_thematiques, clicked_zones):
        # Vérifier si selected_thematiques et clicked_zones ne sont pas None
        if selected_thematiques and 'matrice' in selected_thematiques:
            return generate_sankey_diagram(noms_zones=clicked_zones)
        return html.Div()

    @app.callback(
        Output('volumes', 'children'),
        [Input('selected-thematiques', 'data'),
         Input('clicked-zones', 'data')]
    )
    def update_finances_graph(selected_thematiques, clicked_zones):
        # Vérifier si au moins une des thématiques est sélectionnée
        if selected_thematiques and 'volumes' in selected_thematiques:
            return generate_graph_deplacement(noms_zones=clicked_zones)
        return html.Div()
