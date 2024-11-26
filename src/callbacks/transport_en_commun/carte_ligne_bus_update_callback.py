from dash.dependencies import Input, Output

import plotly.graph_objs as go

from src.data.bus_line_data_process import get_bus_lines_dropdown_options
from src.components.transport_en_commun.bus_carte_element import generate_carte_ligne, create_bus_stops_map_from_xml
from src.components.tableau_de_bord.carte_element import create_default_carte, create_traffic_markers_from_df


def carte_ligne_bus_update_callback(app, prepared_dataframe,gdf_geojson,stops):
    @app.callback(
        Output('selected-affichage', 'data'),
        Input('transport_en_commun-visual-options', 'value')
    )
    def update_store(selected_options):
        return selected_options
    @app.callback(
        Output('transport_en_commun-map', 'figure'),
        [Input('selected-affichage', 'data'),
         Input('ligne-visual-options', 'value'),
         Input('transport_en_commun-line-analyse_par_commune', 'value')]
    )
    def update_figure(selected_affichage,indicateurs,selected_lines):
        fig = go.Figure()
        # Configurer la mise en page de la carte
        fig.update_layout(
            mapbox=dict(
                style='carto-positron',
                center=dict(lat=prepared_dataframe['centroid_lat'].mean(), lon=prepared_dataframe['centroid_lon'].mean()),
                zoom=12
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            hovermode='closest',
            showlegend=False
        )

        if selected_affichage:
            if 'repartition' in selected_affichage:
                fig.add_trace(create_default_carte(gdf_geojson))
            if 'stops' in selected_affichage:
                fig.add_trace(create_bus_stops_map_from_xml(stops))
            if 'point' in selected_affichage:
                traces = create_traffic_markers_from_df()
                fig.add_traces(traces)
        couleur = 'noir'
        traces = generate_carte_ligne(prepared_dataframe, indicateurs,couleur,bus_lines=selected_lines)
        fig.add_traces(traces)

        return fig

    @app.callback(
        Output('selected-transport_en_commun-lines-store', 'data'),  # Le Store à mettre à jour
        Input('transport_en_commun-line-analyse_par_commune', 'value')  # Les valeurs sélectionnées dans le Dropdown
    )
    def store_selected_bus_lines(selected_lines):
        # Si aucune ligne n'est sélectionnée, retourner une liste vide
        if selected_lines is None:
            return []

        # Sinon, retourner les lignes sélectionnées
        return selected_lines


    @app.callback(
        Output('transport_en_commun-line-analyse_par_commune', 'options'),
        Input('transport_en_commun-line-analyse_par_commune', 'id')  # Déclenchement lors du chargement de la page
    )
    def update_bus_lines(_):
        # Récupérer les lignes de transport_en_commun depuis la base de données
        return get_bus_lines_dropdown_options()

    @app.callback(
        [Output('couleur-legend', 'style'),
         Output('left-speed', 'children'),
         Output('right-speed', 'children')],
        [Input('ligne-visual-options', 'value'),
         Input('couleur-legend', 'n_clicks')]
    )
    def update_legend(selected_option, n_clicks):
        # Default legend style
        legend_style = {
            'position': 'absolute',
            'top': '20px',
            'right': '10px',
            'background-color': 'rgba(255, 255, 255, 0.8)',
            'padding': '10px',
            'border-radius': '5px',
            'box-shadow': '0 0 10px rgba(0, 0, 0, 0.1)',
            'z-index': '1000',
            'display': 'flex',
            'align-items': 'center',
            'cursor': 'pointer',
            'transition': 'box-shadow 0.3s ease',
            'visibility': 'hidden'  # Start hidden
        }

        if selected_option:  # Only display if an option is selected
            legend_style['visibility'] = 'visible'

        # Set speed values based on the selected option
        if selected_option == 'nombre_rotation':
            left_speed = "8"
            right_speed = "3"
        elif selected_option == 'nombre_vehicule':
            left_speed = "250"
            right_speed = "20"
        elif selected_option == 'nombre_passager_jour':
            left_speed = "2000"
            right_speed = "60000"
        else:
            left_speed = ""
            right_speed = ""

        return legend_style, left_speed, right_speed