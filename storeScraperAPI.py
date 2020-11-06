import requests
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("API_KEY")

def getCoordinate(street):
    street = street + os.getenv("CITY")
    number = 5000
    coords = []

    while number != 0:
        input = street + " " + str(number)
        formattedInput = input.replace(" ", "%20")
        fields = "name,geometry"

        resp = requests.get(url=f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key={key}&input={formattedInput}&inputtype=textquery&fields={fields}")
        
        coords.append(resp.json()["candidates"][0]["geometry"]["location"])
        streetName = (resp.json()["candidates"][0]["name"])

        if number == 500:
            number = 1
        elif number == 1:
            number -= 1
        else:
            number -= 500

    coordsNoRepeat = []
    for i in range(len(coords)):
        if coords[i] not in coordsNoRepeat:
            coordsNoRepeat.append(coords[i])
    
    return(coordsNoRepeat, streetName)

userStreetName = str(input("Insira a rua para escanear: "))
userNeighborhood = str(input("Insira o bairro: "))
userStreet = userStreetName + " " + userNeighborhood 
spots = getCoordinate(userStreet)
radius = "1000"

placesFound = []

for i in range(len(spots[0])):
    resp = requests.get(url=f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={key}&location={spots[0][i]['lat']},%20{spots[0][i]['lng']}&radius={radius}")
    for i in range(len(resp.json()["results"])):
        placesFound.append({
            "name": resp.json()["results"][i]["name"],
            "location": resp.json()["results"][i]["vicinity"]
        })
        
if len(placesFound) == 0:
    print("Não há comércios nessa região")
else:
    aux = 0
    for i in range(len(placesFound)):
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB"),
            auth_plugin = "mysql_native_password"
        )

        cursor = db.cursor()

        for i in range(len(placesFound)):
            currentName = placesFound[i]['name'].replace(" ", "_").replace("'", "")
            currentStreet = placesFound[i]['location'].replace(" ", "_").replace("'", "").split(",")[0]
            currentLocation = placesFound[i]['location'].replace(" ", "_").replace("'", "")

            cursor.execute(f"INSERT INTO places (place_name, place_street, place_location) VALUES ('{currentName}', '{currentStreet}', '{currentLocation}')")
            db.commit()
            aux += 1

    print(f"Registrado {aux} lugares no banco de dados")



