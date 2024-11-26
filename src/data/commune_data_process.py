import pandas as pd

from sqlalchemy import MetaData, Table, select, func

from src.data.utils import get_session


def get_list_commune():
    session = get_session()
    metadata = MetaData()
    try:
        # Charger la vue population
        population_view = Table('vue_population_par_commune', metadata, autoload_with=session.bind)

        # Créer la requête pour obtenir les noms des communes distincts
        query = select(population_view.c.nom_commune).distinct()

        # Exécuter la requête et récupérer les résultats
        result = session.execute(query).fetchall()

        # Extraire les noms des communes
        commune_names = [row.nom_commune for row in result]

        return commune_names
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Fonction pour obtenir les informations de population par commune depuis la vue
def get_population_commune(commune):
    """
    Récupère les données de population pour une commune spécifique,
    en regroupant les valeurs si la commune a plusieurs entrées.
    """
    metadata = MetaData()
    session = get_session()
    df = None

    try:
        # Charger la vue
        vue = Table('vue_population_par_commune', metadata, autoload_with=session.bind)

        # Requête pour récupérer les données de la commune spécifique
        query = select(vue).where(vue.c.nom_commune == commune)
        result = session.execute(query)

        # Convertir les résultats en DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if not df.empty:
            # Calculer la population totale pour la commune
            total_population_commune = float(df['total_population'].sum())

            # Calculer le total global de la population pour toutes les communes
            total_population_all_communes_query = select(func.sum(vue.c.total_population))
            total_population_all_communes = session.execute(total_population_all_communes_query).scalar()
            total_population_all_communes = float(total_population_all_communes)

            # Calculer le pourcentage par rapport au total des communes
            population_percentage = round((total_population_commune / total_population_all_communes * 100), 1)

            # Construire le DataFrame final
            df = pd.DataFrame([{
                'commune': commune,
                'population': total_population_commune,
                'population_percentage': population_percentage,
                'rank': None  # Le rang peut être ajouté plus tard si nécessaire
            }])
    finally:
        # Fermer la session
        session.close()

    # Retourner un DataFrame vide si aucun résultat n'a été trouvé
    return df if df is not None else pd.DataFrame()



def get_age_distribution_commune(commune):
    metadata = MetaData()
    session = get_session()
    df_pivot = None

    try:
        vue = Table('vue_population_par_commune', metadata, autoload_with=session.bind)
        query = select(vue).where(vue.c.nom_commune == commune)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if not df.empty:
            df_pivot = df.pivot_table(
                index='nom_commune',
                columns='tranche',
                values='total_population',
                fill_value=0
            ).reset_index()
            df_pivot.rename(columns={'nom_commune': 'commune'}, inplace=True)
    finally:
        session.close()

    return df_pivot if df_pivot is not None else pd.DataFrame()


def get_connections_commune(commune):
    metadata = MetaData()
    session = get_session()
    df_connections = None

    try:
        vue = Table('vue_matrice_od_par_commune', metadata, autoload_with=session.bind)
        query = select(vue).where(vue.c.nom_origine == commune)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if not df.empty:
            most_connected = df.nlargest(5, 'nombre_deplacements')[['nom_destination', 'nombre_deplacements']]
            least_connected = df.nsmallest(5, 'nombre_deplacements')[['nom_destination', 'nombre_deplacements']]

            df_connections = pd.DataFrame({
                'commune': [commune],
                'most_connected': [list(most_connected['nom_destination'])],
                'most_connected_counts': [list(most_connected['nombre_deplacements'])],
                'least_connected': [list(least_connected['nom_destination'])],
                'least_connected_counts': [list(least_connected['nombre_deplacements'])]
            })
    finally:
        session.close()

    return df_connections if df_connections is not None else pd.DataFrame()

def get_typologie_modale_commune(commune):
    metadata = MetaData()
    session = get_session()
    df_pivot = None

    try:
        vue = Table('vue_nombre_vehicules_par_commune', metadata, autoload_with=session.bind)
        query = select(vue).where(vue.c.nom_commune == commune)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if not df.empty:
            df_pivot = df.pivot_table(
                index='nom_commune',
                columns='type_vehicule',
                values='nombre_total',
                fill_value=0
            ).reset_index()
            df_pivot.rename(columns={'nom_commune': 'commune'}, inplace=True)
    finally:
        session.close()

    return df_pivot if df_pivot is not None else pd.DataFrame()


# Fonction detail_commune pour obtenir les détails en utilisant les données dynamiques

def get_attraction_production_commune(commune):
    metadata = MetaData()
    session = get_session()
    df = None

    try:
        vue = Table('vue_productions_attractions', metadata, autoload_with=session.bind)
        query = select(vue).where(vue.c.nom_commune == commune)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if not df.empty:
            df.rename(columns={'nom_commune': 'commune', 'total_attractions': 'attraction', 'total_productions': 'production'}, inplace=True)
            df = df[['commune', 'attraction', 'production']]
    finally:
        session.close()

    return df if df is not None else pd.DataFrame()

def get_all_data_commune(commune):
    """
    Récupère toutes les données nécessaires pour une commune spécifique.
    Les données sont récupérées directement via des fonctions optimisées pour une commune donnée.
    """
    # Charger les données dynamiques pour la commune
    commune_data = get_population_commune(commune)
    age_distribution = get_age_distribution_commune(commune)
    attraction_production = get_attraction_production_commune(commune)
    typologie_modale = get_typologie_modale_commune(commune)
    connections = get_connections_commune(commune)

    # Préparer les données pour alimenter la page
    return {
        "general_info": {
            "population": commune_data['population'].iloc[0],
            "population_percentage": commune_data['population_percentage'].iloc[0],
            "rank": commune_data['rank'].iloc[0]
        },
        "age_distribution": {
            "0-5 ans": age_distribution['0-5 ans'].iloc[0],
            "6-15 ans": age_distribution['6-15 ans'].iloc[0],
            "16-25 ans": age_distribution['16-25 ans'].iloc[0],
            "26-60 ans": age_distribution['26-60 ans'].iloc[0],
            "61 ans et plus": age_distribution['61 ans et plus'].iloc[0]
        },
        "attraction_production": {
            "attraction": attraction_production['attraction'].iloc[0],
            "production": attraction_production['production'].iloc[0]
        },
        "typologie_modale": {
            "Voiture": typologie_modale['Voiture'].iloc[0],
            "Moto": typologie_modale['Moto'].iloc[0],
            "Bus": typologie_modale['Bus'].iloc[0]
        },
        "connections": {
            "most_connected": connections['most_connected'].iloc[0],
            "most_connected_counts": connections['most_connected_counts'].iloc[0],
            "least_connected": connections['least_connected'].iloc[0],
            "least_connected_counts": connections['least_connected_counts'].iloc[0]
        }
    }
