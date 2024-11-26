-- Insérer des données dans matrice_od avec des coefficients aléatoires réduits pour les productions et attractions
INSERT INTO matrice_od (id_origine_commune, id_destination_commune, id_type_vehicule, nombre_deplacements)
SELECT
    origine.id AS id_origine,
    destination.id AS id_destination,
    type_vehicule.id AS id_type_vehicule,  -- Référence au type de véhicule
    ROUND(
        (
            origine.total_population *
                CASE
                    WHEN type_vehicule.id = 1 THEN (0.01 + RANDOM() * 0.01)  -- Entre 1% et 2% pour les voitures en production
                    WHEN type_vehicule.id = 2 THEN (0.005 + RANDOM() * 0.005) -- Entre 0.5% et 1% pour les motos en production
                    WHEN type_vehicule.id = 3 THEN (0.015 + RANDOM() * 0.01)  -- Entre 1.5% et 2.5% pour les transport_en_commun en production
                    ELSE 0
                END
        ) +
        destination.total_population *
            CASE
                WHEN type_vehicule.id = 1 THEN (0.015 + RANDOM() * 0.01)  -- Entre 1.5% et 2.5% pour les voitures en attraction
                WHEN type_vehicule.id = 2 THEN (0.007 + RANDOM() * 0.003) -- Entre 0.7% et 1% pour les motos en attraction
                WHEN type_vehicule.id = 3 THEN (0.02 + RANDOM() * 0.01)   -- Entre 2% et 3% pour les transport_en_commun en attraction
                ELSE 0
            END
    ) AS nombre_deplacements  -- Calcul de 'nombre' basé sur des coefficients réduits pour chaque type de véhicule
FROM
    vue_population_par_commune origine
CROSS JOIN
    vue_population_par_commune destination
CROSS JOIN
    types_vehicules type_vehicule
WHERE
    origine.id <> destination.id;  -- Exclure les déplacements internes


INSERT INTO commune_vehicules (commune_id, type_vehicule_id)
SELECT z.id AS commune_id, tv.id AS type_vehicule_id
FROM commune z
CROSS JOIN types_vehicules tv;