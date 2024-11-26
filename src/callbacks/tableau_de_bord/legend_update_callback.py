from dash import Input, Output, html
from src.components.tableau_de_bord.legende import generate_legend

def legend_update_callback(app):
    @app.callback(
        [Output('population-legend', 'children'),
         Output('segment-legend', 'children'),
         Output('route-legend', 'children'),
         Output('density-legend', 'children')],
        [Input('selected-thematiques', 'data')]
    )
    def update_legends(selected_thematiques):
        # Initialiser les légendes à "N/A" par défaut
        population_legend = html.Div()
        segment_legend = html.Div()
        route_legend = html.Div()
        density_legend = html.Div()

        # Vérifier si selected_thematiques n'est pas None et est itérable
        if selected_thematiques:
            if 'densite' in selected_thematiques:
                couleurs = ['#FFEDA0', '#FEB24C', '#FC4E2A', '#E31A1C', '#BD0026']
                valeurs = ['0- 60,000 habitants', '60,001 - 100,000 habitants', '100,001 - 150,000 habitants',
                           '150,001 - 250,000 habitants', '250,001+ habitants']
                population_legend = generate_legend('Population', couleurs, valeurs, 'densite-legend')

            if 'segment' in selected_thematiques:
                couleurs = ['#440154', '#3B528B', '#21918C', '#5EC962', '#FDE725']
                valeurs = ['100-200 volume/heure', '201-300 volume/heure', '301-500 volume/heure', '501-800 volume/heure', '800+ volume/heure']
                segment_legend = generate_legend('Volume de deplacement',couleurs, valeurs,'segment-legend')

            if 'point' in selected_thematiques:
                couleurs = ['black']
                valeurs = ['Les points noirs dans la ville']
                route_legend = generate_legend('Volume de deplacement',couleurs, valeurs,'point-legend')

        return population_legend, segment_legend, route_legend, density_legend
