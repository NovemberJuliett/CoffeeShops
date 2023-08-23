import json
import requests
from geopy import distance
import folium
from flask import Flask
import os
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def nearest_coffee_shops(shop):
    return shop['distance']


def open_map():
    with open('map.html', encoding="utf8") as file:
        return file.read()


def main():
    with open("coffee.json", "r", encoding='CP1251') as my_file:
        coffee_json = my_file.read()

    load_dotenv()

    coffee_shops = json.loads(coffee_json)

    apikey = os.environ['API_KEY']
    question = (input('Где вы находитесь?'))
    coords = fetch_coordinates(apikey, question)

    list_coffee_shops = []
    for i in coffee_shops:
        new_coffee_shops = dict()
        new_coffee_shops['title'] = i['Name']
        new_coffee_shops['distance'] = distance.distance(coords[::-1], [i["Latitude_WGS84"], i["Longitude_WGS84"]]).km
        new_coffee_shops['latitude'] = i["Latitude_WGS84"]
        new_coffee_shops['longitude'] = i["Longitude_WGS84"]
        list_coffee_shops.append(new_coffee_shops)

    sorted_by_distance = sorted(list_coffee_shops, key=nearest_coffee_shops)
    five_coffee_shops = sorted_by_distance[:5]

    tooltip = "Click me!"

    coffee_map = folium.Map(location=coords[::-1], zoom_start=12, tiles="Stamen Terrain")
    for i in five_coffee_shops:
        marker = folium.Marker(
            [i["latitude"], i["longitude"]],
            popup="<i>" + i['title'] + "</i>",
            tooltip=tooltip)
        marker.add_to(coffee_map)
    coffee_map.save("map.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'coffee_map', open_map)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
