import json
import random
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import datetime
import numpy as np

from src.data.utils import get_session


def insert_communes(geojson_path):
    session = get_session()

    try:
        # Charger le fichier GeoJSON
        with open(geojson_path, 'r') as f:
            geojson_dict = json.load(f)

        zones = []
        for feature in geojson_dict['features']:
            zone_name = feature['properties'].get('ADM3_EN', 'Inconnu')
            # ensemble_d = feature['properties'].get('ensemble d', '')
            identifiant_commune = feature['properties'].get('ADM3_PCODE', 'Inconnu')
            zones.append({
                "nom_commune": zone_name,
                "identifiant_commune": identifiant_commune
            })

        # Convertir en DataFrame pour l'insertion
        zones_df = pd.DataFrame(zones)

        # Assurez-vous que les colonnes sont du bon type
        zones_df['nom_commune'] = zones_df['nom_commune'].astype(str)
        zones_df['identifiant_commune'] = zones_df['identifiant_commune'].astype(str, errors='ignore')

        # Insérer les données dans la table ZONES
        zones_df.to_sql('commune', session.bind, if_exists='append', index=False)

        session.commit()
        print(f"{len(zones)} zones ont été insérées dans la table ZONES.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Une erreur est survenue lors de l'insertion dans la base de données : {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        print(f"Une erreur inattendue est survenue : {str(e)}")
        raise
    finally:
        session.close()


def insert_fokotany(file_path):
    session = get_session()  # Assume you have a function to get the DB session
    try:
        # Charger la feuille spécifique de l'Excel
        fokotany_data_xlsx = pd.read_excel(file_path, sheet_name='Feuil1')

        # Récupérer toutes les communes depuis la table 'commune'
        result = session.execute(text("SELECT id, LOWER(nom_commune) FROM commune"))
        communes = {row[1]: row[0] for row in result}  # Associer les noms de commune aux ID en minuscule

        # Préparer les données pour l'insertion dans la table fokotany
        fokotany_data = []

        for _, row in fokotany_data_xlsx.iterrows():
            if pd.notnull(row['Nom Fokontany']):
                commune_name = str(row['Commune']).lower()    # Convertir le nom de la commune en minuscule
                print(commune_name)
                id_commune = communes.get(commune_name)  # Obtenir l'ID de la commune associée

                if id_commune:

                    fokotany_data.append({
                        "id_commune": id_commune,
                        "nom_fokotany": row['Nom Fokontany']
                    })

        # Insérer les données dans la table fokotany
        for fokotany_row in fokotany_data:
            session.execute(
                text("INSERT INTO fokotany (id_commune, nom_fokotany) VALUES (:id_commune, :nom_fokotany)"),
                fokotany_row
            )

        # Commit de la transaction
        session.commit()
        print(f"{len(fokotany_data)} enregistrements de fokotany ont été insérés dans la table FOKOTANY.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Une erreur est survenue lors de l'insertion dans la base de données : {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        print(f"Une erreur inattendue est survenue : {str(e)}")
        raise
    finally:
        session.close()


def insert_population_from_excel(file_path):
    session = get_session()
    try:
        # Charger les données de l'Excel
        population_data_xlsx = pd.read_excel(file_path, sheet_name='Feuil1')
        print(population_data_xlsx.columns)

        # Créer un DataFrame pour les données de population
        population_data = []

        # Récupérer toutes les fokontany (ID des fokontany) depuis la table 'fokotany'
        result = session.execute(text("SELECT id, LOWER(nom_fokotany) FROM fokotany"))
        fokontany_map = {row[1]: row[0] for row in result}  # Associer les fokontany aux ID de fokontany en minuscule

        # Récupérer les tranches d'âge depuis la table 'tranche_age'
        tranche_age_map = {
            '0-5 ans': 8,  # Colonne I
            '6-15 ans': 9,  # Colonne J
            '16-25 ans': 10,  # Colonne K
            '26-60 ans': 11,  # Colonne L
            '61 ans et plus': 12  # Colonne M
        }
        result = session.execute(text("SELECT id, LOWER(tranche) FROM tranche_age"))
        tranche_ages = {row[1]: row[0] for row in result}  # Associer les tranches d'âge aux ID en minuscule

        # Générer les données de population pour chaque fokontany et chaque tranche d'âge à partir du fichier Excel
        for _, row in population_data_xlsx.iterrows():
            if pd.notnull(row['Nom Fokontany']):
                fokotany = row['Nom Fokontany'].lower()  # Convertir en minuscule avant comparaison
                id_fokotany = fokontany_map.get(fokotany)  # Obtenir l'ID de fokontany associé

                if id_fokotany:
                    # Insérer les populations pour chaque tranche d'âge en utilisant les indices de colonne
                    for tranche_label, col_index in tranche_age_map.items():
                        id_tranche_age = tranche_ages.get(tranche_label.lower())  # Obtenir l'ID de tranche d'âge

                        # Accéder à la valeur dans la colonne par son index
                        population_count = row.iloc[col_index]
                        print(row.iloc[col_index])

                        # Vérifier si la valeur est numérique, sinon la remplacer par 0
                        if not pd.isna(population_count) and isinstance(population_count, (int, float)):
                            population_count = int(population_count)
                        else:
                            population_count = 0

                        # Ajouter aux données de population si valide
                        if id_tranche_age:
                            population_data.append({
                                "id_fokotany": id_fokotany,
                                "id_tranche_age": id_tranche_age,
                                "nombre_population": population_count,
                                "annee_enregistrement": datetime.datetime.now().year
                            })

        # Convertir en DataFrame pour l'insertion
        population_df = pd.DataFrame(population_data)

        # Insérer les données dans la table 'population'
        population_df.to_sql('population', session.bind, if_exists='append', index=False)

        session.commit()
        print(f"{len(population_data)} enregistrements de population ont été insérés dans la table POPULATION.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Une erreur est survenue lors de l'insertion dans la base de données : {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        print(f"Une erreur inattendue est survenue : {str(e)}")
        raise
    finally:
        session.close()

# def insert_population(xlsx_path):
#     try:
#         # Lire le fichier Excel
#         population_df = pd.read_excel(xlsx_path)
#
#         # Vérifier et adapter les colonnes si nécessaire
#         population_df['idpopulation'] = population_df['idpopulation'].astype(str)
#         population_df['idzone'] = population_df['idzone'].astype(str)
#         population_df['feminine'] = population_df['feminine'].astype(int)
#         population_df['masculine'] = population_df['masculine'].astype(int)
#
#         # Insérer les données dans la table POPULATION
#         with get_engine().connect() as connection:
#             population_df.to_sql('population', connection, if_exists='append', index=False)
#
#         print(f"{len(population_df)} enregistrements ont été insérés dans la table POPULATION.")
#
#     except SQLAlchemyError as e:
#         print(f"Une erreur est survenue lors de l'insertion dans la base de données : {str(e)}")
#     except Exception as e:
#         print(f"Une erreur inattendue est survenue : {str(e)}")

# def insert_matriceOD():
#     session = get_session()  # Fonction qui doit retourner une session SQLAlchemy
#     try:
#         # Récupérer tous les ID de zones et types de véhicules
#         idzones = [row[0] for row in session.execute(text("SELECT id FROM commune"))]
#         idvehicules = [row[0] for row in session.execute(text("SELECT id FROM types_vehicules"))]
#
#         matrice_od_data = []
#
#         for _ in range(20):  # Insérer 20 enregistrements fictifs
#             id_origine = random.choice(idzones)
#             id_destination = random.choice(idzones)
#             while id_origine == id_destination:  # Assurez-vous que l'origine et la destination ne sont pas identiques
#                 id_destination = random.choice(idzones)
#
#             id_type_vehicule = random.choice(idvehicules)
#             nombre = random.randint(1, 100)  # Générer un nombre aléatoire de déplacements
#
#             matrice_od_data.append({
#                 "id_origine": id_origine,
#                 "id_destination": id_destination,
#                 "id_type_vehicule": id_type_vehicule,
#                 "nombre": nombre
#             })
#
#         # Convertir en DataFrame pour l'insertion
#         matrice_od_df = pd.DataFrame(matrice_od_data)
#
#         # Insérer les données dans la table matrice_od
#         matrice_od_df.to_sql('matrice_od', session.bind, if_exists='append', index=False)
#
#         session.commit()
#         print(f"{len(matrice_od_data)} enregistrements ont été insérés dans la table matrice_od.")
#     except SQLAlchemyError as e:
#         session.rollback()
#         print(f"Une erreur est survenue lors de l'insertion dans la base de données : {str(e)}")
#         raise
#     except Exception as e:
#         session.rollback()
#         print(f"Une erreur inattendue est survenue : {str(e)}")
#         raise
#     finally:
#         session.close()

def insert_vehicules():
    session = get_session()
    try:
        # Liste des types de véhicules à insérer
        vehicules = [
            {"id": 1, "nom_type": "Voiture"},
            {"id": 2, "nom_type": "Moto"},
            {"id": 3, "nom_type": "Bus"},
        ]

        # Convertir en DataFrame pour l'insertion
        vehicules_df = pd.DataFrame(vehicules)

        # Insérer les données dans la table TYPEVEHICULE
        vehicules_df.to_sql('types_vehicules', session.bind, if_exists='append', index=False)

        session.commit()
        print(f"{len(vehicules)} types de véhicules ont été insérés dans la table TYPEVEHICULE.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Une erreur est survenue lors de l'insertion dans la base de données : {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        print(f"Une erreur inattendue est survenue : {str(e)}")
        raise
    finally:
        session.close()


def insert_hierarchie_fonctionnelle():
    session = get_session()
    try:
        niveaux = ["primary", "secondary", "tertiary"]
        hierarchie_data = [{"nom_niveau": niveau} for niveau in niveaux]

        hierarchie_df = pd.DataFrame(hierarchie_data)

        # Insérer les données dans la table 'hierarchie_fonctionnelle'
        hierarchie_df.to_sql('hierarchie_fonctionnelle', session.bind, if_exists='append', index=False)

        session.commit()
        print(f"{len(hierarchie_data)} enregistrements ont été insérés dans la table hierarchie_fonctionnelle.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Erreur lors de l'insertion dans la table hierarchie_fonctionnelle : {str(e)}")
        raise
    finally:
        session.close()

def insert_routes_from_geojson_with_hierarchy(geojson_path):
    session = get_session()
    try:
        # Charger le fichier GeoJSON
        with open(geojson_path, 'r') as f:
            geojson_dict = json.load(f)

        # Exécuter la requête pour obtenir le mapping de la hiérarchie fonctionnelle
        result = session.execute(text("SELECT id, nom_niveau FROM hierarchie_fonctionnelle"))

        # Créer un dictionnaire de mapping entre 'nom_niveau' et 'id'
        hierarchie_mapping = {row[1]: row[0] for row in result}  # row[1] est 'nom_niveau', row[0] est 'id'

        route_data = []

        # Parcourir les features du GeoJSON pour extraire les informations nécessaires
        for feature in geojson_dict['features']:
            id_OSM = feature['properties'].get('osm_id')
            nom_niveau = feature['properties'].get('highway')
            id_hierarchie = hierarchie_mapping.get(nom_niveau)

            # Ajouter les données à la liste si les conditions sont remplies
            if id_OSM is not None and id_hierarchie is not None:
                route_data.append({
                    "id_hierarchie": id_hierarchie,
                    "id_osm": id_OSM
                })

        # Convertir la liste en DataFrame pour l'insertion dans la base de données
        route_df = pd.DataFrame(route_data)

        # Insérer les données dans la table 'route'
        route_df.to_sql('route', session.bind, if_exists='append', index=False)

        # Valider les changements
        session.commit()

    except SQLAlchemyError as e:
        # Rollback en cas d'erreur SQL
        session.rollback()
        print(f"Erreur lors de l'insertion dans la table route : {str(e)}")
        raise

    except Exception as e:
        # Rollback en cas d'erreur générale
        session.rollback()
        print(f"Erreur inattendue : {str(e)}")
        raise

    finally:
        # Fermer la session
        session.close()

def insert_flux_trafic():
    session = get_session()
    try:
        idroute = [row[0] for row in session.execute(text("SELECT id FROM route"))]
        idmodes = [row[0] for row in session.execute(text("SELECT id FROM types_vehicules"))]
        idperiodes = [row[0] for row in session.execute(text("SELECT id FROM periodes_temps"))]

        flux_data = []

        for _ in range(20):
            id_origine = random.choice(idroute)
            id_destination = random.choice(idroute)
            while id_origine == id_destination:
                id_destination = random.choice(idroute)
            id_mode = random.choice(idmodes)
            id_periode_temps = random.choice(idperiodes)
            volume = random.randint(50, 1000)
            date = datetime.datetime.now().date()
            vitesse_moyenne = round(random.uniform(30.0, 120.0), 2)
            temps_de_trajet = round(random.uniform(5.0, 60.0), 2)
            distance = round(random.uniform(1.0, 100.0), 2)

            flux_data.append({
                "id_departed": id_origine,
                "id_arrived": id_destination,
                "id_type_vehicule": id_mode,
                "id_periode_temps": id_periode_temps,
                "volume_deplacement": volume,
                "date": date,
                "vitesse_moyenne": vitesse_moyenne,
                "temps_de_trajet": temps_de_trajet,
                "distance": distance
            })

        flux_df = pd.DataFrame(flux_data)

        # Insérer les données dans la table 'flux_trafic'
        flux_df.to_sql('flux_trafic', session.bind, if_exists='append', index=False)

        session.commit()
        print(f"{len(flux_data)} enregistrements ont été insérés dans la table flux_trafic.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Erreur lors de l'insertion dans la table flux_trafic : {str(e)}")
        raise
    finally:
        session.close()




def insert_cooperatives(data):
    """
    Insère les coopératives dans la table 'cooperatives'.
    Retourne un dictionnaire associant le nom de la coopérative à son ID.
    """
    session = get_session()

    cooperative_map = {}

    try:
        for cooperative in data['cooperative'].unique():
            if cooperative:
                # Vérifier si la coopérative existe déjà
                result = session.execute(
                    text("SELECT id FROM cooperatives WHERE nom_cooperative = :cooperative"),
                    {"cooperative": cooperative}
                ).fetchone()

                if result:
                    cooperative_id = result[0]
                else:
                    # Insérer la coopérative si elle n'existe pas encore
                    session.execute(
                        text("INSERT INTO cooperatives (nom_cooperative) VALUES (:cooperative)"),
                        {"cooperative": cooperative}
                    )
                    # Récupérer l'ID de la coopérative nouvellement insérée
                    cooperative_id = session.execute(
                        text("SELECT id FROM cooperatives WHERE nom_cooperative = :cooperative"),
                        {"cooperative": cooperative}
                    ).fetchone()[0]

                cooperative_map[cooperative] = cooperative_id

        session.commit()
        print("Coopératives insérées avec succès.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Une erreur est survenue lors de l'insertion des coopératives : {str(e)}")
        raise
    finally:
        session.close()

    return cooperative_map


def insert_lignes(data):
    """
    Insère les lignes de transport_en_commun dans la table 'lignes'.
    """
    session = get_session()

    try:
        for _, row in data.iterrows():
            # Récupérer l'ID de la coopérative associée
            result = session.execute(
                text("SELECT id FROM cooperatives WHERE nom_cooperative = :cooperative"),
                {"cooperative": row['cooperative']}
            ).fetchone()

            if result:
                id_cooperative = result[0]

                # Vérifier si la ligne existe déjà
                ligne_result = session.execute(
                    text("SELECT id FROM lignes WHERE numero_ligne = :numero_ligne AND id_cooperative = :id_cooperative"),
                    {"numero_ligne": row['ligne'], "id_cooperative": id_cooperative}
                ).fetchone()

                if not ligne_result:
                    # Insérer la ligne si elle n'existe pas encore
                    session.execute(
                        text("""
                            INSERT INTO lignes (numero_ligne, id_cooperative, nombre_antennes)
                            VALUES (:numero_ligne, :id_cooperative, 1)
                        """),
                        {"numero_ligne": row['ligne'], "id_cooperative": id_cooperative}
                    )

        session.commit()
        print("Lignes de transport_en_commun insérées avec succès.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Une erreur est survenue lors de l'insertion des lignes : {str(e)}")
        raise
    finally:
        session.close()


def insert_antennes(data):
    """
    Insère les informations sur les antennes (données de transport_en_commun) dans la table 'antenne'.
    Remplace les valeurs numériques NaN par la médiane de chaque colonne.
    """
    session = get_session()

    # Calcul des médianes pour les colonnes numériques
    median_values = {
        'nombre_arret': data['nombre_arret'].median(),
        'Nombre_Bus': data['Nombre_Bus'].median(),
        'rotation': data['rotation'].median(),
        'Consommation_totale': data['Consommation_totale'].median(),
        'nombre_passager': data['nombre_passager'].median(),
        'distance_primus_terminus': data['distance_primus_terminus'].median(),
        'distance_aller_retour': data['distance_aller_retour'].median(),
        'heure_exploitation': data['heure_exploitation'].median()
    }

    try:
        for _, row in data.iterrows():
            # Récupérer l'ID de la coopérative associée
            cooperative_result = session.execute(
                text("SELECT id FROM cooperatives WHERE nom_cooperative = :cooperative"),
                {"cooperative": row['cooperative']}
            ).fetchone()

            if cooperative_result:
                id_cooperative = cooperative_result[0]

                # Récupérer l'ID de la ligne associée
                ligne_result = session.execute(
                    text("""
                        SELECT id FROM lignes
                        WHERE numero_ligne = :numero_ligne AND id_cooperative = :id_cooperative
                    """),
                    {"numero_ligne": row['ligne'], "id_cooperative": id_cooperative}
                ).fetchone()

                if ligne_result:
                    ligne_id = ligne_result[0]

                    # Remplacer les NaN par les médianes calculées pour éviter les erreurs
                    nombre_arret = int(row['nombre_arret']) if not np.isnan(row['nombre_arret']) else int(
                        median_values['nombre_arret'])
                    nombre_vehicule = int(row['Nombre_Bus']) if not np.isnan(row['Nombre_Bus']) else int(
                        median_values['Nombre_Bus'])
                    nombre_rotation = int(row['rotation']) if not np.isnan(row['rotation']) else int(
                        median_values['rotation'])
                    consomation_jour = float(row['Consommation_totale']) if not np.isnan(
                        row['Consommation_totale']) else float(median_values['Consommation_totale'])
                    nombre_passager_jour = int(row['nombre_passager']) if not np.isnan(row['nombre_passager']) else int(
                        median_values['nombre_passager'])
                    nombre_bus_jour = int(row['Nombre_Bus']) if not np.isnan(row['Nombre_Bus']) else int(
                        median_values['Nombre_Bus'])

                    # Nouvelles colonnes avec médiane si NaN
                    primus = row['primus'] if pd.notna(row['primus']) else ""
                    terminus = row['terminus'] if pd.notna(row['terminus']) else ""
                    distance_primus_terminus = float(row['distance_primus_terminus']) if not np.isnan(
                        row['distance_primus_terminus']) else float(median_values['distance_primus_terminus'])
                    distance_aller_retour = float(row['distance_aller_retour']) if not np.isnan(
                        row['distance_aller_retour']) else float(median_values['distance_aller_retour'])
                    heure_exploitation = int(row['heure_exploitation']) if not np.isnan(
                        row['heure_exploitation']) else int(median_values['heure_exploitation'])

                    # Vérification des limites pour nombre_passager_jour
                    nombre_passager_jour = min(max(nombre_passager_jour, 0), 9223372036854775807)

                    # Insérer les données de l'antenne
                    session.execute(
                        text("""
                            INSERT INTO antenne (
                                numero_ligne, primus, terminus, distance_primus_terminus,
                                distance_aller_retour, nombre_arret, nombre_vehicule, nombre_rotation,
                                consomation_jour, nombre_passager_jour, nombre_bus_jour, heure_exploitation
                            ) VALUES (
                                :numero_ligne, :primus, :terminus, :distance_primus_terminus,
                                :distance_aller_retour, :nombre_arret, :nombre_vehicule, :nombre_rotation,
                                :consomation_jour, :nombre_passager_jour, :nombre_bus_jour, :heure_exploitation
                            )
                        """),
                        {
                            "numero_ligne": ligne_id,
                            "primus": primus,
                            "terminus": terminus,
                            "distance_primus_terminus": distance_primus_terminus,
                            "distance_aller_retour": distance_aller_retour,
                            "nombre_arret": nombre_arret,
                            "nombre_vehicule": nombre_vehicule,
                            "nombre_rotation": nombre_rotation,
                            "consomation_jour": consomation_jour,
                            "nombre_passager_jour": nombre_passager_jour,
                            "nombre_bus_jour": nombre_bus_jour,
                            "heure_exploitation": heure_exploitation
                        }
                    )

        session.commit()
        print("Antennes insérées avec succès.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Une erreur est survenue lors de l'insertion des antennes : {str(e)}")
        raise
    finally:
        session.close()

