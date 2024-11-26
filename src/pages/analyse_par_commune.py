from dash import dcc
import dash_bootstrap_components as dbc

# Import de la fonction get_commune_names pour récupérer les noms des communes
from src.data.commune_data_process import get_list_commune

# Charger les noms de communes depuis la vue
commune_names = get_list_commune()  # Appel à la fonction pour obtenir les communes

# Construire les options du dropdown
commune_options = [{'label': name, 'value': name} for name in commune_names]

# Layout de la page avec le dropdown
def detail_zone(app):
    return dbc.Container([
        # Dropdown pour sélectionner une commune
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='commune-dropdown',
                    options=commune_options,
                    value=commune_names[0] if commune_names else None,
                    placeholder="Sélectionnez une commune",
                    style={'width': '100%'}
                ),
                width=12
            )
        ], className="mb-4"),

        dbc.Row(id='zone-detail-content')
    ], fluid=True, style={'margin': '20px', 'background-color': '#f9f9f9', 'padding': '20px', 'border-radius': '8px'})


