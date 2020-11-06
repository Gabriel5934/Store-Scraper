import requests
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("API_KEY")

def getCoordinate(street):
    input = street + os.getenv("CITY")
    formattedInput = input.replace(" ", "%20")
    fields = "name,geometry"

    resp = requests.get(url=f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key={key}&input={formattedInput}&inputtype=textquery&fields={fields}")
    
    coords = (resp.json()["candidates"][0]["geometry"]["location"])
    streetName = (resp.json()["candidates"][0]["name"])
    
    return(coords)

userStreetName = str(input("Insira a rua para escanear: "))
userNeighborhood = str(input("Insira o bairro: "))
userStreet = userStreetName + " " + userNeighborhood 
spots = getCoordinate(userStreet)

placesFound = []
number = 5000

while number != 0:
    resp = requests.get(url=f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={key}&location={spots['lat']},%20{spots['lng']}&radius={number}")
    for i in range(len(resp.json()["results"])):
        placesFound.append({
            "name": resp.json()["results"][i]["name"],
            "location": resp.json()["results"][i]["vicinity"]
        })
        
    if number == 500:
        number = 1
    elif number == 1:
        number -= 1
    else:
        number -= 500

if len(placesFound) == 0:
    print("Não há comércios nessa região")
else:
    placesFoundNoRepeat = []
    for i in range(len(placesFound)):
        if placesFound[i] not in placesFoundNoRepeat:
            placesFoundNoRepeat.append(placesFound[i])

    for i in range(len(placesFoundNoRepeat)):
        print(placesFoundNoRepeat[i]["name"])
    
    print(len(placesFoundNoRepeat))

    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB"),
        auth_plugin = "mysql_native_password"
    )

    aux = 0
    for i in range(len(placesFoundNoRepeat)):
        cursor = db.cursor()
        currentName = placesFoundNoRepeat[i]['name'].replace(" ", "_").replace("'", "")
        currentStreet = placesFoundNoRepeat[i]['location'].replace(" ", "_").replace("'", "").split(",")[0]
        currentLocation = placesFoundNoRepeat[i]['location'].replace(" ", "_").replace("'", "")

        cursor.execute(f"INSERT INTO places2 (place_name, place_street, place_location) VALUES ('{currentName}', '{currentStreet}', '{currentLocation}')")
        db.commit()
        aux += 1

    cursor = db.cursor()
    cursor.execute('''
        DELETE t1 FROM places2 t1
        INNER JOIN places2 t2 
        WHERE 
            t1.place_id < t2.place_id AND 
            t1.place_name = t2.place_name;
    ''')
    db.commit()
        
    print(f"Registrado {aux - cursor.rowcount} lugares no banco de dados")



