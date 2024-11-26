from dash import Output, Input

from src.pages.accueil import accueil
from src.pages.transport_en_commun import bus
from src.pages.tableau_indicateur_ligne_bus import bus_outil
from src.pages.analyse_par_commune import detail_zone
from src.pages.tableau_de_bord import tableau_de_bord_layout
from src.pages.detail_ligne_bus import ligne_detail
from src.pages.reference import reference
from src.pages.comparaison_scenario import scenario


def page_content_update_callback(app):
    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/analyse_par_commune':
            return detail_zone(app)
        elif pathname == '/comparaison_scenario':
            return scenario()
        elif pathname == '/reference':
            return reference()
        elif pathname == '/transport_en_commun':
            return bus()
        elif pathname == '/outil_bus':
            return bus_outil(app)
        elif pathname and pathname.startswith('/details'):
            return detail_zone(app)
        elif pathname and pathname.startswith('/detail_bus/'):
            ligne_id = pathname.split('/')[-1]  # Extraire l'ID de la ligne de transport_en_commun depuis l'URL
            return ligne_detail(ligne_id)  # Affiche la page de détails
        elif pathname == '/bord':
            return tableau_de_bord_layout()
        else:
            return accueil()


