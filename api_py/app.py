
import base64
import io
import pandas as pd
import folium
from flask import Flask
from folium.plugins.marker_cluster import MarkerCluster
import matplotlib.pyplot as plt
import openrouteservice
import json
import polyline
import requests
from flask import Flask, request, jsonify
import math
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
app = Flask(__name__)
d = pd.read_csv("new_2022.csv")
d = d.loc[d['nom'] == 'Gazole']
client = openrouteservice.Client(key='5b3ce3597851110001cf6248ef96e5f27bcc4bcd989bc39299e5060b')

# partie MC
def getPrixCarburant(date="06/02/2023", cp=75):
    PrixCarburant = pd.read_csv("new_2022.csv")
    data = PrixCarburant.loc[PrixCarburant['nom'] == 'Gazole']
    #Supprimer moi les data avec valeur < 1
    data = data.loc[data['valeur'] > 1]
    #Supprimer moi les data avec valeur < 1
    data = data.loc[data['valeur'] < 3.50]
    data.maj = pd.to_datetime(data.maj)
    data.maj = data.maj.map(dt.datetime.toordinal)
    Y = data.valeur.to_numpy()
    X = data[['departement', 'maj']].to_numpy()
    # Création des listes pour les données des colonnes
    departement = [cp]
    maj = [date]
    # Création du DataFrame à partir des listes
    df = pd.DataFrame({'departement': departement, 'maj': maj})
    df.maj = pd.to_datetime(df.maj)
    df.maj = df.maj.map(dt.datetime.toordinal)
    varaible_input = df[['departement', 'maj']].to_numpy()
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3)
    regressor = LinearRegression()
    regressor.fit(X_train, Y_train)
    Y_pred = regressor.predict(X_test)
    Y_pred = regressor.predict(varaible_input)
    return Y_pred[0]

def getSingleStation(date="06/02/2023",ad=""):
    # Charger les données
    PrixCarburant = pd.read_csv("new_2022.csv")
    # Filtrer les données pour le type de carburant 'Gazole' et les valeurs entre 1 et 3.50
    data = PrixCarburant.loc[(PrixCarburant['nom'] == 'Gazole') & (PrixCarburant['valeur'] > 1) & (PrixCarburant['valeur'] < 3.50)]
    # Convertir la colonne 'maj' en représentation ordinale
    data['maj'] = pd.to_datetime(data['maj'])
    data['maj'] = data['maj'].map(dt.datetime.toordinal)
    # Filtrer les données pour l'adresse 'ZA Les Touzelleries'
    data = data.loc[data['adresse'] == ad]
    # Séparer les données en variable cible et en caractéristiques d'entrée
    Y = data['valeur'].to_numpy()
    X = data[['maj']].to_numpy()
    # Définir la date de prédiction et la convertir en représentation ordinale
    prediction_date = date
    df = pd.DataFrame({'maj': [prediction_date]})
    df['maj'] = pd.to_datetime(df['maj'])
    df['maj'] = df['maj'].map(dt.datetime.toordinal)
    varaible_input = df[['maj']].to_numpy()
    # Entraîner le modèle
    regressor = LinearRegression()
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=0)
    regressor.fit(X_train, Y_train)
    Y_pred_date = regressor.predict(varaible_input)
    # Faire la prédiction
    Y_pred = regressor.predict(X_test)
    return Y_pred.min()

def coordonnees():    
    currentPosition = request.json['currentPosition']
    destination = request.json['destination']
    dataDepar = getGeoCode(currentPosition)
    dataArrive = getGeoCode(destination)
    depart = float(dataDepar['lon']), float(dataDepar['lat'])
    arrivee =  float(dataArrive['lon']), float(dataArrive['lat'])
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
    if coords == []:
        coords.append(decoded[len(decoded)-1])       
    return coords   

def station_arret(decoded, m):
    arret = arret_plein(decoded, m)    
    liste_arret = []
    for i in range(0, len(arret)):
        for j in range(0, len(d)):
            if haversine(arret[i][0], arret[i][1], float(d.latitude[j]), float(d.longitude[j])) < 5:
                liste_arret.append(d)
                folium.Circle(
                [float(d.latitude[j]), float(d.longitude[j])],
                popup=str(d.adresse[j]) + "\n" + str(d.valeur[j]),
                color='red',
                ).add_to(m)
    return liste_arret            
def getListStation(decoded, m):
    arret = arret_plein(decoded, m)    
    liste_arret = []
    address_to_value = {}
    for i in range(0, len(arret)):
        temp_lists = []
        temp_address = []
        for j in range(0, len(d)):
            if haversine(arret[i][0], arret[i][1], float(d.latitude[j]), float(d.longitude[j])) < 5:
                address = d.adresse[j]
                value = float(d.valeur[j])
                lat = float(d.latitude[j])
                lon = float(d.longitude[j])
                if address in address_to_value:
                    address_to_value[address]['sum'] += value
                    address_to_value[address]['count'] += 1
                else:
                    address_to_value[address] = {'sum': value, 'count': 1}
        for address, values in address_to_value.items():
            average = values['sum'] / values['count']
            temp_lists.append([address, average, lat, lon])
        cheapest = min(temp_lists, key=lambda x: x[1])
        temp_address.append([arret[i][0],arret[i][1], cheapest[0], cheapest[1], cheapest[2], cheapest[3]])
        liste_arret.append(temp_address)
    return liste_arret
def haversine(lat1, lon1, lat2, lon2):
    R = 6371 # radius of earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
def getDistanceArret(dataDepar, dataArrive, tempStation):
    distanceArr = []
    for i in range(0, len(tempStation)):
        if i == 0:
            distance0 = haversine(float(dataDepar['lat']),float(dataDepar['lon']), float(tempStation[i][0][0]), float(tempStation[i][0][1]))
            distanceArr.append(distance0)
        distanceI = haversine(float(tempStation[i-1][0][0]), float(tempStation[i-1][0][1]), float(tempStation[i][0][0]), float(tempStation[i][0][1]))
        distanceArr.append(distanceI)
        if i == len(tempStation)-1:
            distanceFin = haversine(float(dataArrive['lat']),float(dataArrive['lon']), float(tempStation[i][0][0]), float(tempStation[i][0][1]))
            distanceArr.append(distanceFin)
    return distanceArr 
def getPrixOptimals(tempStation, distanceArr,date, cpDepar, cpArrive):
    prixOptimal = []
    for i in range(0, len(distanceArr)):
        if i == 0:
            prix0 = getPrixCarburant(date, cpDepar)
            prixOptimal.append(prix0)
        if i == len(distanceArr)-1:
            prixFin = getPrixCarburant(date, cpArrive)
            prixOptimal.append(prixFin)
        if i != 0 and i != len(distanceArr)-1: 
            prixI = getSingleStation(date, str(tempStation[i-1][0][2]))
            prixOptimal.append(prixI)
    return prixOptimal
def getPrixOptimalTotal(prixOptimal, distanceArr):
    prixTotalOptimal = 0
    for i in range(0, len(prixOptimal)):
        prixTotalOptimal = prixTotalOptimal + prixOptimal[i]*distanceArr[i]
    prixTotalOptimal = prixTotalOptimal/4.7 
    return prixTotalOptimal

def getGeoCode(address):
    nominatim_url = f'https://nominatim.openstreetmap.org/search?addressdetails=1&q={address}&format=json&limit=1'
    response = requests.get(nominatim_url)
    data = response.json()
    if len(data) > 0:
        postal_code = data[0]['address']['postcode']
        lat = data[0]['lat']
        lon = data[0]['lon']
        data = {'postal_code': postal_code, 'lat': lat, 'lon': lon}
        return data
    else:
        return None

def trajetMap(date,cpDepar, cpArrive,  dataDepar, dataArrive):    
    #coordonnées de départ et d'arrivée du GPS
    #openrouteservice prend les coordonnées dans l'ordre (lon, lat) et non (lat, lon) comme pour folium
    #on inverse donc les coordonnées avec depart_reverse et arrivee_reverse
    depart = (float(dataDepar['lon']), float(dataDepar['lat']))
    depart_reverse = (float(dataDepar['lat']), float(dataDepar['lon']))
    arrivee = (float(dataArrive['lon']), float(dataArrive['lat']))
    arrivee_reverse = (float(dataArrive['lat']), float(dataArrive['lon']))
    #on regroupe les coordonnées dans un tuple
    coords = ((depart, arrivee))
    #appelle de la fonction directions de openrouteservice
    res = client.directions(coords)

    #test our response
    with(open('trajet.json','+w')) as f:
        f.write(json.dumps(res,indent=4, sort_keys=True))
    geometry = client.directions(coords)['routes'][0]['geometry']
    decoded = polyline.decode(geometry)
  
    m = folium.Map(location=depart_reverse,zoom_start=10, control_scale=True,tiles="cartodbpositron")
    #on affiche le trajet sur la carte avec la distance et le temps de parcours 
    distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+" Km </strong>" +"</h4></b>"
    duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['duration']/60,1))+" Mins. </strong>" +"</h4></b>"
    folium.PolyLine(decoded).add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)
    
    #on affiche le point de départ et d'arrivée sur la carte
    folium.Marker(
    location=depart_reverse,
    popup="Depart",
    icon=folium.Icon(color="green"),
    ).add_to(m)

    folium.Marker(
    location=arrivee_reverse,
    popup="Arrivee",
    icon=folium.Icon(color="red"),
    ).add_to(m)
    #on affiche les arrêts sur la carte
    arret_plein(decoded, m)
    station_arret(decoded, m)
    tempStation = getListStation(decoded, m)
    distanceArr = getDistanceArret(dataDepar, dataArrive, tempStation)
    prixOptimal = getPrixOptimals(tempStation, distanceArr, date, cpDepar, cpArrive)
    for i in range(0, len(distanceArr)):
        if i == 0:
            folium.Circle(
                [float(dataDepar['lat']), float(dataDepar['lon'])],
                popup="Départ"+ "\n" + "Prix: " + str(prixOptimal[i]) + "€/L",
                color='blue',
                ).add_to(m)
        if i == len(distanceArr)-1:
            folium.Circle(
                [float(dataArrive['lat']), float(dataArrive['lon'])],
                popup="Arrivée"+ "\n" + "Prix: " + str(prixOptimal[i]) + "€/L",
                color='blue',
                ).add_to(m)
        if i != 0 and i != len(distanceArr)-1:
            folium.Circle(
                [float(tempStation[i-1][0][4]), float(tempStation[i-1][0][5])],
                popup="Arrêt plein: " +  "\n" + str(tempStation[i-1][0][2]) + "\n" + str(tempStation[i-1][0][3])+ "€/L",
                color='blue',
                ).add_to(m)
    m.save('map.html')
    return m._repr_html_()

@app.route('/trajet_map', methods=['POST'])
def trajet_map():
    currentPosition = request.json['currentPosition']
    destination = request.json['destination']
    date = request.json['date']
    dataDepar = getGeoCode(currentPosition)
    dataArrive = getGeoCode(destination)
    cpDepar = int(dataDepar['postal_code'][:2])
    cpArrive = int(dataArrive['postal_code'][:2])
    mapHtml = trajetMap(date,cpDepar,cpArrive, dataDepar, dataArrive)
    return mapHtml
@app.route('/prixoptimal', methods=['POST'])
def distanceNew():
    currentPosition = request.json['currentPosition']
    destination = request.json['destination']
    date = request.json['date']
    dataDepar = getGeoCode(currentPosition)
    dataArrive = getGeoCode(destination)
    cpDepar = int(dataDepar['postal_code'][:2])
    cpArrive = int(dataArrive['postal_code'][:2])
    depart = float(dataDepar['lon']), float(dataDepar['lat'])
    arrivee =  float(dataArrive['lon']), float(dataArrive['lat'])
    coords = ((depart, arrivee))
    res = client.directions(coords)
    distanceTotal = round(res['routes'][0]['summary']['distance']/1000)
    tempStation = getListStation(decode(coords), folium.Map())
    #calcul de la distance entre chaque arrêt
    distanceArr = getDistanceArret(dataDepar, dataArrive,tempStation)
    #fin calcul de la distance entre chaque arrêt
    #calcul du prix optimal
    prixOptimal = getPrixOptimals(tempStation, distanceArr,date, cpDepar, cpArrive)
    #fin calcul du prix optimal
    prixTotalOptimal = getPrixOptimalTotal(prixOptimal, distanceArr)
    #calcul du distanceTotal
    #fin calcul du distanceTotal
    data = {
    'prixTotalOptimal':prixTotalOptimal,
    'distanceTotal':distanceTotal,
    'prixOptimal':prixOptimal,
    'distanceArr':distanceArr
      }
    return data
if __name__ == '__main__':
    app.run(debug=True) 