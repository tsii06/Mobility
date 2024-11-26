import pandas as pd

from sqlalchemy import MetaData, Table, select, func, insert

from src.data.utils import get_session

def fetch_scenarios_from_db():
    session = get_session()
    metadata = MetaData()

    try:
        # Chargement de la vue 'scenario_full_view'
        vue = Table('vue_scenario', metadata, autoload_with=session.bind)

        # Requête pour sélectionner toutes les données
        query = select(vue)
        result = session.execute(query)

        # Conversion des résultats en DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

    finally:
        session.close()
def insert_scenario_data(nom, description, type_scenario, date_simulation,
                         debit_moyen, vitesse_moyenne, temps_trajet_moyen, volume_carburant_simule,
                         longueur_trajet_moyenne, co2, nox, co):
    session = get_session()
    metadata = MetaData()

    # Charger les tables
    scenario_table = Table('comparaison_scenario', metadata, autoload_with=session.bind)
    scenario_detail_table = Table('scenario_detail_indicateur', metadata, autoload_with=session.bind)
    scenario_detail_env_table = Table('scenario_detail_environement', metadata, autoload_with=session.bind)

    try:
        # Insérer dans la table `comparaison_scenario`
        new_scenario = insert(scenario_table).values(
            nom_scenario=nom,
            description_scenario=description,
            type_scenario=type_scenario,
            date_simulation=date_simulation
        )
        result = session.execute(new_scenario)

        # Obtenir l'ID du scénario inséré
        scenario_id = result.inserted_primary_key[0]

        # Insérer dans la table `scenario_detail`
        new_scenario_detail = insert(scenario_detail_table).values(
            id_scenario=scenario_id,
            debit_moyen=debit_moyen,
            vitesse_moyenne=vitesse_moyenne,
            temps_trajet_moyen=temps_trajet_moyen,
            volume_carburant_simule=volume_carburant_simule,
            longueur_trajet_moyenne=longueur_trajet_moyenne
        )
        session.execute(new_scenario_detail)

        # Insérer dans la table `scenarnio_detail_envrionement`
        new_scenario_detail_env = insert(scenario_detail_env_table).values(
            id_scenario=scenario_id,
            co2=co2,
            nox=nox,
            co=co
        )
        session.execute(new_scenario_detail_env)

        # Valider toutes les transactions
        session.commit()
        print("Données insérées avec succès.")

    except SQLAlchemyError as e:
        # Annuler la transaction en cas d'erreur
        session.rollback()
        print(f"Erreur lors de l'insertion : {e}")
    finally:
        session.close()


def get_all_scenarios():
    session = get_session()
    metadata = MetaData()

    try:
        # Chargement de la vue 'scenario_full_view'
        vue = Table('vue_scenario', metadata, autoload_with=session.bind)

        # Requête pour sélectionner toutes les données de la vue
        query = select(vue)

        # Exécution de la requête
        result = session.execute(query)

        # Conversion en DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

    finally:
        session.close()


def fetch_two_most_recent_scenarios():
    """
    Récupère les deux scénarios les plus récents dans la base de données.
    """
    session = get_session()
    metadata = MetaData()

    try:
        # Chargement de la vue 'scenario_full_view'
        vue = Table('vue_scenario', metadata, autoload_with=session.bind)

        # Requête pour récupérer les deux scénarios les plus récents
        query = select(vue).order_by(vue.c.date_simulation.desc()).limit(2)
        result = session.execute(query)

        # Conversion en DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

    finally:
        session.close()

