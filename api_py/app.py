
import base64
import io
import math
import pandas as pd
import folium
from flask import Flask
from folium.plugins.marker_cluster import MarkerCluster
import matplotlib.pyplot as plt
import openrouteservice
import json
import polyline
from geopy.distance import geodesic as geo

app = Flask(__name__)
es = pd.read_csv('test.csv', sep=';')
es = es.drop(columns=['id','horaires', 'prix_id', 'services_service', 'horaires_automate_24_24', 'epci_code', 'epci_name', 'reg_code', 'com_name', 'com_code'], axis=1)
print(es.shape)
print(es.dtypes)
list(es)
lat = []
lon = []
for line in es.geom:
    geo = line.split(",")
    lat.append(geo[0])
    lon.append(geo[1])

es["latitude"] = lat
es["longitude"] = lon
client = openrouteservice.Client(key='5b3ce3597851110001cf6248ef96e5f27bcc4bcd989bc39299e5060b')    

depart = (float(lon[0]), float(lat[0]))
arrivee = (float(lon[1]), float(lat[1]))
depart_reverse = (float(lat[0]), float(lon[0]))
arrivee_reverse = (float(lat[1]), float(lon[1]))

@app.route('/hitmap')
def map(): 
    map = folium.Map(location=[48.78, 2.17], zoom_start=7, )

    for i in range(0, len(es)):
        lat = es.latitude[i]
        lon = es.longitude[i]
        prix = es.prix_valeur[i]

        if prix < 1.0:
            folium.Circle(
            radius=5,
            location=[lat, lon],
            color='lime',
            fill=False,).add_to(map)

        elif prix < 1.5:
            folium.Circle(
            radius=5,
            location=[lat, lon],
            color='yellow',
            fill=False,).add_to(map)

        elif prix < 2.0:
            folium.Circle(
            radius=5,
            location=[lat, lon],
            color='pink',
            fill=False,).add_to(map)

        elif prix >= 2.0:
            folium.Circle(
            radius=5,
            location=[lat, lon],
            color='red',
            fill=False,).add_to(map)

    return map._repr_html_()

@app.route('/graph')
def graph():

    Normandie = 0
    Corse = 0
    Bretagne = 0
    Occitanie = 0
    CVL = 0
    GE = 0
    NA = 0
    ARA = 0
    PACA = 0
    IDF = 0
    PDL = 0
    HDF = 0
    BFC = 0

    labels = 'Normandie', 'Corse', 'Bretagne', 'Occitanie', 'Grand Est', 'Centre-Val de Loire', 'Nouvelle-Aquitaine', 'Auvergne-Rhône-Alpes', "PACA", 'IDF', 'Pays de la Loire', 'HDF', 'BFC'
    for i in es.reg_name:
        if i == 'Normandie':
            Normandie=Normandie+1
        if i == 'Corse':
            Corse=Corse+1
        if i == 'Bretagne':
            Bretagne=Bretagne+1
        if i == 'Occitanie':
            Occitanie=Occitanie+1  
        if i == 'Centre-Val de Loire':
            CVL=CVL+1      
        if i == 'Grand Est':
            GE=GE+1  
        if i == 'Nouvelle-Aquitaine':
            NA=NA+1  
        if i == 'Auvergne-Rhône-Alpes':
            ARA=ARA+1  
        if i == "Provence-Alpes-Côte d'Azur":
            PACA=PACA+1 
        if i == 'Île-de-France':
            IDF=IDF+1  
        if i == 'Pays de la Loire':
            PDL=PDL+1  
        if i == 'Hauts-de-France':
            HDF=HDF+1  
        if i == 'Bourgogne-Franche-Comté':
            BFC=BFC+1  

    sizes = [Normandie, Corse, Bretagne, Occitanie, GE, CVL, NA, ARA, PACA, IDF, PDL, HDF, BFC]
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'purple', 'red', 'green', 'yellow', 'orange', 'brown', 'lime', 'pink', 'magenta']

    img = io.BytesIO()

    plt.pie(sizes, labels=labels, colors=colors, 
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')   
    plt.savefig(img, format='png')
    

    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return '<img src="data:image/png;base64,{}">'.format(plot_url)

@app.route('/table')
def table():

    SP98 = 0
    SP95 = 0
    Gazole = 0
    E10 = 0
    E85 = 0
    GPLc = 0
    nan = 0

    names = ['SP98', 'SP95', 'Gazole', 'E10', 'E85', 'GPLc', "nan"]
    for i in es.prix_nom:
        if i == 'SP98':
            SP98=SP98+1
        if i == 'SP95':
            SP95=SP95+1
        if i == 'Gazole':
            Gazole=Gazole+1
        if i == 'E10':
            E10=E10+1
        if i == 'E85':
            E85=E85+1
        if i == 'GPLc':
            GPLc=GPLc+1
        if i == 'nan':
            nan=nan+1  

    values = [SP98, SP95, Gazole, E10, E85, GPLc, nan]
    img = io.BytesIO()

    plt.figure(figsize=(20, 3))

    plt.subplot(131)
    plt.plot(names, values)
    plt.suptitle('Type carburant')

    plt.savefig(img, format='png')

    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return '<img src="data:image/png;base64,{}">'.format(plot_url)  

def coordonnees():    
    coords = ((depart, arrivee))
    return coords

def decode(coords):
    geometry = client.directions(coords)['routes'][0]['geometry']
    decoded = polyline.decode(geometry)
    return decoded

def arret_plein(decoded, m):
    coords = []
    for i in range(1, len(decoded)):
        if i%2500 == 0:
            coords.append(decoded[i])
            folium.Marker(
            location=decoded[i],
            popup="Arrêt plein\n" + str(decoded[i]),
            icon=folium.Icon(color="blue"),
            ).add_to(m)
    return coords        

@app.route('/map')
def mapping():
  
    coords = coordonnees()
    res = client.directions(coords)
    decoded = decode(coords)
    m = folium.Map(location=depart_reverse,zoom_start=10, control_scale=True,tiles="cartodbpositron")
    #on affiche le trajet sur la carte avec la distance et le temps de parcours 
    distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+" Km </strong>" +"</h4></b>"
    duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['duration']/60,1))+" Mins. </strong>" +"</h4></b>"
    folium.PolyLine(decoded).add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)
    
    #on affiche le point de départ et d'arrivée sur la carte
    folium.Marker(
    location=depart_reverse,
    popup=es.adresse[0] +" "+ es.ville[0]+" "+ str(es.cp[0]),
    icon=folium.Icon(color="green"),
    ).add_to(m)

    folium.Marker(
    location=arrivee_reverse,
    popup=es.adresse[1] +" "+ es.ville[1]+" "+ str(es.cp[1]),
    icon=folium.Icon(color="red"),
    ).add_to(m)

    #on affiche les arrêts sur la carte
    arrets = arret_plein(decoded, m)

    m.save('map.html')
    return m._repr_html_()

#calculer la distance entre le trajet et les stations
def distance(lat1, lon1, lat2, lon2):
    R = 6373.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return distance
         
