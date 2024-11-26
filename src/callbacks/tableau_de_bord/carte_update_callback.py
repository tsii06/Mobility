from dash.dependencies import Input, Output

from src.components.tableau_de_bord.carte_element import create_density_carte, create_default_carte, create_route, \
    create_traffic_markers, create_route_with_traffic, \
    create_route_with_traffic_colored, create_traffic_markers_from_df
import plotly.graph_objs as go


def carte_update_callback(app, gdf_merged, gdf_geojson,lats, lons,congestion,df_filtered):
    @app.callback(
        Output('map', 'figure'),
        [Input('selected-thematiques', 'data')]
    )
    def update_figure(selected_thematiques):
        fig = go.Figure()

        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=-18.8792, lon=47.5079),
                zoom=12
            ),
            paper_bgcolor="lightgrey",
            showlegend=False,
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        fig.add_trace(create_route(lats, lons))
        if selected_thematiques:
            if 'densite' in selected_thematiques:
                fig.add_trace(create_density_carte(gdf_merged))

            if 'segment' in selected_thematiques:
                fig.add_trace(create_traffic_markers(congestion))

            if 'itineraire' in selected_thematiques:
                traces = create_route_with_traffic_colored(df_filtered)
                fig.add_traces(traces)

            if 'congestion' in selected_thematiques:
                traces = create_route_with_traffic(df_filtered)
                fig.add_traces(traces)

            if 'point' in selected_thematiques:
                traces = create_traffic_markers_from_df()
                fig.add_traces(traces)



        else:
            fig.add_trace(create_default_carte(gdf_geojson))

        return fig
