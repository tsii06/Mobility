import pandas as pd

from sqlalchemy import MetaData, Table, select, func

from src.data.utils import get_session


def get_population_par_commune(noms_communes=None):
    # Initialiser la session
    session = get_session()
    metadata = MetaData()

    try:
        # Charger la vue vue_population_par_commune
        vue_population = Table('vue_population_par_commune', metadata, autoload_with=session.bind)

        # Construire la requête
        if noms_communes:
            # Filtrer selon les noms des communes spécifiés
            query = select(vue_population).where(
                func.lower(vue_population.c.nom_commune).in_([nom.lower() for nom in noms_communes])
            )
        else:
            # Récupérer les 8 communes avec le plus grand nombre de population, en ordre croissant
            query = select(vue_population).order_by(vue_population.c.total_population.desc()).limit(30)

        # Exécuter la requête
        result = session.execute(query)
        # Convertir les résultats en DataFrame Pandas
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        return df
    finally:
        # Fermer la session
        session.close()



# Ce fonction permet d'avoir le volume de deplacement par zone(entrée et sortie)
def get_volume_deplacements(noms_zones=None):
    session = get_session()
    metadata = MetaData()

    try:
        vue = Table('vue_productions_attractions', metadata, autoload_with=session.bind)
        if noms_zones:
            query = select(vue).where(func.lower(vue.c.nom_commune).in_([nom.lower() for nom in noms_zones]))

        else:
            query = select(vue).order_by(vue.c.total_volume.desc()).limit(8)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    finally:
        session.close()

# Ce fonction permet d'avoir le nombre de vehicule par type et  par zone
def get_nombre_vehicules_par_zone(noms_zones=None):
    metadata = MetaData()
    session = get_session()
    df = None  # Initialiser df à None pour éviter les erreurs de portée

    try:
        vue = Table('vue_nombre_vehicules_par_commune', metadata, autoload_with=session.bind)
        if noms_zones:
            query = select(vue).where(func.lower(vue.c.nom_commune).in_([nom.lower() for nom in noms_zones]))
        else:
            query = select(vue)  # Supprimer le limit ici pour l'appliquer après le tri

        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Tri des données par 'nom_commune' pour garantir un ordre uniforme
        df.sort_values(by=['nom_commune', 'type_vehicule'], ascending=True, inplace=True)

        # Appliquer une limite après le tri
        df = df.head(15)
    finally:
        session.close()

    # Vérifier que df contient bien des données avant de le retourner
    if df is not None:
        return df
    else:
        return pd.DataFrame()  # Retourner un DataFrame vide si la requête échoue


def create_od_matrix(df_matrice):
    od_matrix = df_matrice.pivot_table(
        index='nom_origine',
        columns='nom_destination',
        values='nombre_deplacements',
        fill_value=0
    ).reset_index()
    return od_matrix

# fonction pour avoir le nombre de deplacement entre origine destination
def get_od_count(noms_zones=None):
    metadata = MetaData()
    session = get_session()
    try:
        vue = Table('vue_matrice_od_par_commune', metadata, autoload_with=session.bind)
        if noms_zones:
            query = select(vue).where(func.lower(vue.c.nom_origine).in_([nom.lower() for nom in noms_zones]))
        else:
            query = select(vue).order_by(vue.c.nombre_deplacements.desc()).limit(10)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

    finally:
        session.close()

