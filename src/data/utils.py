import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_CONFIG
from shapely import Point
import geopandas as gpd
from sqlalchemy import MetaData,Table,select
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
import io


gdf = gpd.read_file(r"data/Antananarivo_voiries_primaires-secondaires-tertiaire.geojson")

# Fonction pour obtenir l'objet engine
def get_engine():
    db_url = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"
    return create_engine(db_url)


# Fonction pour obtenir une session
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def find_zone_by_coordinates(lat, lon, gdf_communes):
    point = Point(lon, lat)
    for _, row in gdf_communes.iterrows():
        if row['geometry'].contains(point):
            return row['identifiant_commune']
    return None

def extract_lat_lon():
    gdf_filtered = gdf[gdf['highway'].isin(['primary', 'secondary', 'tertiary'])]
    gdf_filtered = gdf_filtered.to_crs(epsg=3857)
    gdf_filtered = gdf_filtered.to_crs(epsg=4326)
    lats, lons = [], []
    for geom in gdf_filtered.geometry:
        if geom.geom_type == 'MultiLineString':
            for line in geom.geoms:
                lons.extend([coord[0] for coord in line.coords] + [None])
                lats.extend([coord[1] for coord in line.coords] + [None])
        elif geom.geom_type == 'LineString':
            lons.extend([coord[0] for coord in geom.coords] + [None])
            lats.extend([coord[1] for coord in geom.coords] + [None])
    return lats, lons


def loadGeojson():
    geojson_path = r"data/limites_communes_ANTANANARIVO.geojson"
    gdf_geojson = gpd.read_file(geojson_path)
    if gdf_geojson.crs != "EPSG:4326":
        gdf_geojson = gdf_geojson.to_crs(epsg=4326)

    return gdf_geojson


def create_excel(dataframe):
    # Convertir le DataFrame en fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.getvalue()



