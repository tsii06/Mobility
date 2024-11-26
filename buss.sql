CREATE database buss;
\c buss;

CREATE TABLE commune (
    id SERIAL PRIMARY KEY,
    nom_commune VARCHAR(255) NOT NULL,  -- Nom de la commune géographique
    identifiant_commune VARCHAR(50) NOT NULL
);

CREATE TABLE periodes_temps (
    id SERIAL PRIMARY KEY,
    nom_periode VARCHAR(255) NOT NULL
);

insert into periodes_temps values(default,'matin'),(default,'soir');

CREATE TABLE tranche_age (
id SERIAL PRIMARY KEY,
tranche VARCHAR(50) NOT NULL,  -- Description de la tranche d'âge (ex: "0-5 ans")
age_min INTEGER NOT NULL,  -- Âge minimum de la tranche d'âge
age_max INTEGER NOT NULL   -- Âge maximum de la tranche d'âge
);

INSERT INTO tranche_age (tranche, age_min, age_max)
VALUES
('0-5 ans', 0, 5),  -- Enfants et adolescents
('6-15 ans', 6, 15),  -- Jeunes (adolescents et jeunes adultes)
('16-25 ans', 16, 25),  -- Population active (adulte)
('26-60 ans', 26, 60),
('61 ans et plus', 61, 120);

create table fokotany(
    id SERIAL PRIMARY KEY,
    id_commune INTEGER REFERENCES commune(id), 
    nom_fokotany VARCHAR(100)   
);

CREATE TABLE population (
    id SERIAL PRIMARY KEY,
    id_fokotany INTEGER REFERENCES fokotany(id), 
    id_tranche_age INTEGER NOT NULL REFERENCES tranche_age(id),  -- Référence à la tranche d'âge
    annee_enregistrement INTEGER NOT NULL,  -- Année de la donnée de population
    nombre_population INTEGER NOT NULL  -- Nombre d'hommes dans la commune
);



CREATE TABLE types_vehicules (
    id SERIAL PRIMARY KEY,
    nom_type VARCHAR(255) NOT NULL
);



CREATE TABLE matrice_od (
    id SERIAL PRIMARY KEY,
    id_origine_commune INTEGER REFERENCES commune(id),  -- Référence à la commune d'origine
    id_destination_commune INTEGER REFERENCES commune(id),  -- Référence à la commune de destination
    id_type_vehicule INTEGER REFERENCES types_vehicules(id),  -- Référence au type de véhicule
    nombre_deplacements INTEGER NOT NULL  -- Nombre de déplacements pour cette combinaison
);

CREATE TABLE hierarchie_fonctionnelle (
    id SERIAL PRIMARY KEY,
    nom_niveau VARCHAR(255) NOT NULL  -- Nom de la hiérarchie (ex : "Autoroute", "Route Principale", "Route Secondaire")
);

CREATE TABLE route(
   id SERIAL PRIMARY KEY,
   id_hierarchie INTEGER REFERENCES hierarchie_fonctionnelle(id),
   id_OSM VARCHAR(50)
);

CREATE TABLE flux_trafic (
    id SERIAL PRIMARY KEY,
    id_departed INTEGER REFERENCES route(id),
    id_arrived INTEGER REFERENCES route(id),
    id_type_vehicule INTEGER REFERENCES types_vehicules(id),
    id_periode_temps INTEGER REFERENCES periodes_temps(id),
    volume_deplacement INTEGER NOT NULL,
    date DATE NOT NULL,
    vitesse_moyenne DECIMAL(5, 2),
    temps_de_trajet DECIMAL(5, 2),
    distance DECIMAL(10, 2)  
);


-- Table pour les informations sur les coopératives
CREATE TABLE cooperatives (
    id SERIAL PRIMARY KEY,
    nom_cooperative VARCHAR(50) NOT NULL
);

CREATE table lignes(
    id serial PRIMARY KEY,
    numero_ligne VARCHAR(10),
    id_cooperative INT REFERENCES cooperatives(id),
    nombre_antennes int
);

-- Table pour les informations sur les véhicules
CREATE TABLE antenne (
    id SERIAL PRIMARY KEY,
    numero_ligne INT REFERENCES lignes(id),
    primus VARCHAR(50),
    terminus VARCHAR(50),
    distance_primus_terminus DECIMAL(10,2),
    distance_aller_retour DECIMAL(10,2),
    nombre_arret INT,
    nombre_vehicule INT,
    nombre_rotation INT,
    consomation_jour DECIMAL(10, 2),
    nombre_passager_jour BIGINT,
    heure_exploitation int,
    nombre_bus_jour INT,
    date_enquette date
);


create table variable_calcul(
    prix_carburant DECIMAL(6,2),
    frais_passager DECIMAL(6,2),
    ammortissement DECIMAL(6,2),
    salaire_receveur_chauffeur DECIMAL(6,2)
);

create table scenario(
    id serial PRIMARY KEY,
    nom_scenario VARCHAR(50),
    description_scenario VARCHAR(100),
    type_scenario VARCHAR(50),
    date_simulation date
);

create table scenario_detail_indicateur(
    id_scenario int REFERENCES scenario(id),
    debit_moyen DECIMAL(6,2),
    vitesse_moyenne DECIMAL(6,2),
    temps_trajet_moyen DECIMAL(6,2),
    volume_carburant_simule DECIMAL(6,2),
    longueur_trajet_moyenne DECIMAL(6,2)
);

create table scenario_detail_environement(
    id_scenario int REFERENCES scenario(id),
    co2 DECIMAL(6,2),
    nox DECIMAL(6,2),
    co DECIMAL(6,2)
);




CREATE OR REPLACE VIEW vue_population_par_commune AS
SELECT 
    c.id,
    c.nom_commune,
    c.identifiant_commune,
    p.id_tranche_age,
    ta.tranche,
    ta.age_min,
    ta.age_max,
    SUM(p.nombre_population) AS total_population
FROM 
    commune c
    JOIN fokotany f ON c.id = f.id_commune
    JOIN population p ON f.id = p.id_fokotany
    JOIN tranche_age ta ON p.id_tranche_age = ta.id  -- Jointure avec la table tranche_age
GROUP BY 
    c.id, c.nom_commune, c.identifiant_commune, p.id_tranche_age, ta.tranche, ta.age_min, ta.age_max
ORDER BY 
    c.nom_commune, p.id_tranche_age;



CREATE VIEW vue_productions_attractions AS
   SELECT
       z.id AS commune_id,
       z.nom_commune,
       COALESCE(SUM(CASE WHEN m.id_origine_commune = z.id THEN m.nombre_deplacements ELSE 0 END), 0) AS total_productions,
       COALESCE(SUM(CASE WHEN m.id_destination_commune = z.id THEN m.nombre_deplacements ELSE 0 END), 0) AS total_attractions,
       COALESCE(SUM(CASE WHEN m.id_origine_commune = z.id THEN m.nombre_deplacements ELSE 0 END), 0) +
       COALESCE(SUM(CASE WHEN m.id_destination_commune = z.id THEN m.nombre_deplacements ELSE 0 END), 0) AS total_volume
   FROM
       commune z
   LEFT JOIN
       matrice_od m ON z.id = m.id_origine_commune OR z.id = m.id_destination_commune
   GROUP BY
       z.id, z.nom_commune;

CREATE TABLE commune_vehicules (
    id SERIAL PRIMARY KEY,
    commune_id INTEGER NOT NULL REFERENCES commune(id), -- Référence à la commune
    type_vehicule_id INTEGER NOT NULL REFERENCES types_vehicules(id) -- Référence au type de véhicule
);

-- Insérer les combinaisons de chaque commune avec chaque type de véhicule



-- Création de la table résultante si nécessaire
CREATE or REPLACE view vue_nombre_vehicules_par_commune AS
SELECT
    zv.commune_id,
    z.nom_commune,
    zv.type_vehicule_id,
    tv.nom_type AS type_vehicule,
    COALESCE(SUM(mo.nombre_deplacements), 0) AS nombre_total
FROM
    commune_vehicules zv
LEFT JOIN
    commune z ON zv.commune_id = z.id
LEFT JOIN
    types_vehicules tv ON zv.type_vehicule_id = tv.id
LEFT JOIN
    matrice_od mo ON zv.commune_id = mo.id_origine_commune AND zv.type_vehicule_id = mo.id_type_vehicule
GROUP BY
    zv.commune_id,
    z.nom_commune,
    zv.type_vehicule_id,
    tv.nom_type
ORDER BY
    zv.commune_id;  

CREATE VIEW vue_matrice_od_par_vehicule AS
SELECT
    mo.id,
    mo.id_origine_commune,
    zo.nom_commune AS nom_origine,
    mo.id_destination_commune,
    zd.nom_commune AS nom_destination,
    mo.id_type_vehicule,
    t.nom_type as type_vehicule,
    mo.nombre_deplacements
FROM
    matrice_od mo
JOIN
    commune zo ON mo.id_origine_commune = zo.id
JOIN
    commune zd ON mo.id_destination_commune = zd.id
 JOIN
 	types_vehicules t ON t.id = mo.id_type_vehicule;



CREATE VIEW vue_matrice_od_par_commune AS
SELECT 
    nom_origine,
    nom_destination,
    sum(nombre_deplacements) AS nombre_deplacements,
    (SELECT SUM(nombre_deplacements) 
     FROM vue_matrice_od_par_vehicule
     WHERE vue_matrice_od_par_vehicule.nom_origine = v.nom_origine) AS somme_totale_par_origine
FROM 
    vue_matrice_od_par_vehicule v
GROUP BY 
    nom_origine, nom_destination;


CREATE VIEW vue_volume_deplacement_par_route AS
WITH total_volume AS (
    SELECT
        id_departed AS route_id,
        SUM(volume_deplacement) AS total_volume
    FROM
        flux_trafic
    GROUP BY
        id_departed
    
    UNION ALL
    
    SELECT
        id_arrived AS route_id,
        SUM(volume_deplacement) AS total_volume
    FROM
        flux_trafic
    GROUP BY
        id_arrived
)
SELECT
    tv.route_id,
    r.id_osm,
    SUM(tv.total_volume) AS total_traffic_volume
FROM
    total_volume tv
JOIN
    route r ON tv.route_id = r.id
GROUP BY
    tv.route_id, r.id_osm
ORDER BY
    total_traffic_volume DESC;


CREATE VIEW vue_cooperative_ligne_antenne AS
SELECT 
    c.id AS cooperative_id,
    c.nom_cooperative,
    l.numero_ligne,
    l.nombre_antennes,
    a.id,
    a.primus,
    a.terminus,
    a.distance_primus_terminus,
    a.distance_aller_retour,
    a.nombre_arret,
    a.nombre_vehicule,
    a.nombre_rotation,
    a.consomation_jour,
    a.nombre_passager_jour,
    a.heure_exploitation,
    a.nombre_bus_jour
FROM 
    cooperatives c
    JOIN lignes l ON c.id = l.id_cooperative
    JOIN antenne a ON l.id = a.numero_ligne;


CREATE VIEW vue_scenario AS
SELECT 
    s.id AS id_scenario,
    s.nom_scenario ,
    s.description_scenario,
    s.type_scenario,
    s.date_simulation,
    sd.debit_moyen,
    sd.vitesse_moyenne,
    sd.temps_trajet_moyen,
    sd.volume_carburant_simule,
    sd.longueur_trajet_moyenne,
    se.co2,
    se.nox,
    se.co
FROM 
    scenario s
LEFT JOIN 
    scenario_detail_indicateur sd ON s.id = sd.id_scenario
LEFT JOIN 
    scenario_detail_environement se ON s.id = se.id_scenario;

