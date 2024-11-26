from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from src.callbacks.tableau_de_bord.carte_interactions_callback import carte_interaction_callback, plein_ecran_carte
from src.callbacks.transport_en_commun.carte_ligne_bus_update_callback import carte_ligne_bus_update_callback
from src.callbacks.tableau_de_bord.graphique_update_callback import graphique_update_callback
from src.callbacks.tableau_de_bord.legend_update_callback import legend_update_callback
from src.callbacks.transport_en_commun.indicateurs_bus_callback import indicateurs_bus_callback
from src.callbacks.navigation_page.page_content_update_callback import page_content_update_callback
from src.callbacks.comparaison_scenario.navigation_scenario_content_callback import navigation_scenarion_content_callback
from src.callbacks.comparaison_scenario.insertion_scenario_callback import insertion_scenario_callback
from src.callbacks.analyse_par_commune.detail_commune_callback import detail_commune_callback
from src.components.header import header

from src.callbacks.tableau_de_bord.carte_update_callback import carte_update_callback
from src.callbacks.tableau_de_bord.option_visualisation_interaction_callback import option_visualisation_interaction_callback
from src.data.ETL.extract_geojson_data import loadRepartitionZonale
from src.data.bus_line_data_process import get_geo_data_all_ligne
from src.data.carte_data_process import get_merged_geo_population_data, get_volume_deplacement_route

from src.data.utils import extract_lat_lon
from src.components.transport_en_commun.bus_carte_element import process_transport_geometry
from src.components.tableau_de_bord.carte_element import load_and_prepare_traffic_data

# Remplacez par le chemin de votre répertoire
ligne_geo_data = get_geo_data_all_ligne()
prepared_dataframe = process_transport_geometry(ligne_geo_data)
gdf_merged = get_merged_geo_population_data()
gdf_geojson = loadRepartitionZonale()
lats, lons = extract_lat_lon()
congestion =get_volume_deplacement_route()
df_filtre = load_and_prepare_traffic_data(
        geojson_path=r"data/Antananarivo_voiries_primaires-secondaires-tertiaire.geojson",
        traffic_data_function=get_volume_deplacement_route
    )
stops = r"data/bus_lines_and_stops.xml"

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'], suppress_callback_exceptions=True)
app.layout = html.Div([
    header(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={"marginTop": "2px", "overflowY": "hidden"}), # Désactive le défilement vertical pour cet élément
    html.Div(id='dd')
])

# loadCallback
carte_update_callback(app, gdf_merged,gdf_geojson,lats, lons,congestion,df_filtre)
graphique_update_callback(app)
option_visualisation_interaction_callback(app)
page_content_update_callback(app)
carte_interaction_callback(app,gdf_merged)
legend_update_callback(app)
plein_ecran_carte(app)
navigation_scenarion_content_callback(app)
indicateurs_bus_callback(app)
insertion_scenario_callback(app)
carte_ligne_bus_update_callback(app,prepared_dataframe,gdf_geojson,stops)
detail_commune_callback(app)

server = app.server
if __name__ == '__main__':
    # get_resource_usage()
    app.run_server(debug=True)
