
import pandas as pd
import folium
from flask import Flask
from folium.plugins.marker_cluster import MarkerCluster
app = Flask(__name__)

@app.route('/hitmap')
def hello():
    #lecture du fichier "fromage.txt" avec la fonction read_table de pandas
    #header = 0, la première ligne correspond à l'entête (intitulé des champs)
    es = pd.read_csv('test.csv', sep=';')
    #afficher les dimensions de la table  (fonction shape) ainsi que leur types (propriété dtype)
    es = es.drop(columns=['id','horaires', 'prix_id', 'services_service', 'horaires_automate_24_24', 'epci_code', 'epci_name', 'reg_code', 'com_name', 'com_code'], axis=1)
    print(es.shape)
    #afficher la liste des colonnes et leurs types avec la fonction dtypes
    print(es.dtypes)
    #afficher les 4 premières ligne de la table
    list(es)
    
    lat = []
    lon = []

    for line in es.geom:
        geo = line.split(",")
        lat.append(geo[0])
        lon.append(geo[1])

    es["latitude"] = lat
    es["longitude"] = lon

    map = folium.Map(location=[48.78, 2.17], zoom_start=15, )

    es.apply(lambda row:folium.Circle(radius=5, color='red',location=[row["latitude"], row["longitude"]]).add_to(map), axis=1) 
    return map._repr_html_()


