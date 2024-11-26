import pandas as pd


def extractKodatuDataBus():
    # Chemin vers le fichier Excel
    file_path = r"data/Codatu_BDD lignes existantes_202407.xlsx"

    # Charger la feuille "transport_en_commun urbain" en sautant les deux premières lignes et en utilisant la troisième comme en-tête
    bus_urbain_clean_df = pd.read_excel(file_path, sheet_name='bus urbain', header=2)

    # Supprimer les colonnes qui sont complètement vides
    bus_urbain_clean_df.dropna(axis=1, how='all', inplace=True)

    # Supprimer la première ligne de données et créer une copie explicite pour éviter SettingWithCopyWarning
    bus_urbain_clean_df = bus_urbain_clean_df.iloc[1:].copy()

    # Sélectionner les colonnes par leur numéro d'index et copier les données
    columns_of_interest_indices = [
        0,  # ligne
        1,  # cooperative
        4,  # primus
        5,  # terminus
        7,  # distance primus_terminus
        8,  # distance aller_retour
        9,  # nombre arret
        12, # passage par zone d'activite
        15, # intermodalite rocade
        16, # nombre transport_en_commun
        25, # age parc moyen
        31, # rotation
        35, # heure de travail
        36, # heure de travail
        37  # nombre passager
    ]
    columns_of_interest = bus_urbain_clean_df.iloc[:, columns_of_interest_indices].copy()

    # Renommer les colonnes avec des noms appropriés
    columns_of_interest.columns = [
        'ligne',
        'cooperative',  # Nom de la coopérative
        'primus',  # Primus (Point de départ)
        'terminus',  # Terminus (Point d'arrivée)
        'distance_primus_terminus',  # Distance entre les points de départ et d'arrivée
        'distance_aller_retour',
        'nombre_arret',  # Nombre d'arrêts
        'passsage_zone',  # Heures de travail
        'intermodalite_rocade',  # Intermodalité Rocade
        'Nombre_Bus',  # Nombre de transport_en_commun
        'Age_Moyen_Parc',  # Âge moyen du parc
        'rotation',
        'heure_travail',
        'heure_exploitation',
        'nombre_passager'
    ]


    # Identifier les colonnes qui parlent de la consommation de carburant (par ex., celles contenant "L/100 km")
    consumption_columns = [col for col in bus_urbain_clean_df.columns if "L/100" in col]

    # Extraire les colonnes de consommation uniquement
    consumption_data = bus_urbain_clean_df[consumption_columns].copy()

    # Remplacer les valeurs manquantes par 0 et convertir les données en types appropriés
    consumption_data.fillna(0, inplace=True)
    consumption_data = consumption_data.infer_objects(copy=False)

    # Ajouter la somme des consommations sous une nouvelle colonne 'Consommation'
    columns_of_interest['Consommation'] = consumption_data.sum(axis=1)
    # La consommation est en L/100 km, donc nous devons ajuster pour la distance réelle parcourue
    total_distance = columns_of_interest['distance_aller_retour'] * columns_of_interest[
        'rotation']
    columns_of_interest['Consommation_totale'] = (total_distance* columns_of_interest['Consommation']) / 100


    # Sélectionner toutes les lignes sauf la dernière
    columns_of_interest = columns_of_interest.iloc[:-1, :]
    columns_of_interest['ligne'] = columns_of_interest['ligne'].astype(str)

    # Retourner le DataFrame filtré avec des noms de colonnes simplifiés
    return columns_of_interest
