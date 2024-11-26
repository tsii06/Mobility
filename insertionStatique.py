from src.data.ETL.extract_excel_data import extractKodatuDataBus
from src.data.ETL.insertion import *

regionale = r"data/limites_communes_ANTANANARIVO.geojson"
route = r"data/Antananarivo_voiries_primaires-secondaires-tertiaire.geojson"
population = r"data/Fokontany_population_tranche.xlsx"
# Lire une feuille spécifique du fichier Excel

insert_communes(regionale)
insert_fokotany(population)
insert_population_from_excel(population)
insert_vehicules()

insert_hierarchie_fonctionnelle()

insert_routes_from_geojson_with_hierarchy(route)

insert_flux_trafic()


data = extractKodatuDataBus()

# Étape 1 : Insérer les coopératives
cooperative_map = insert_cooperatives(data)

# Étape 2 : Insérer les lignes
insert_lignes(data)

# Étape 3 : Insérer les antennes
insert_antennes(data)

