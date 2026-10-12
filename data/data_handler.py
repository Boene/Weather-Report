import json
from pathlib import Path
from src.api import get_data
from data.map_values import city_coords

DATA_FILE = Path(__file__).resolve().parent / "weather_data" / "recent_values.jsonl"

### Append 1 line - representing data for 1 city - to the JSONL file

def append_recent(data: dict, city: str):
    data["city"] = city
    with open(DATA_FILE, "a", encoding="utf-8") as datei:
        datei.write(json.dumps(data, ensure_ascii=False) + "\n")

### Load recent data for given city

def load_recent_city(city: str):
    with open(DATA_FILE, "r", encoding="utf-8") as datei:
        for zeile in datei:
            data_line = json.loads(zeile)
            if data_line["city"] == city:
                return data_line
        return {}       ### needs better handling! just there to calm down linting ###

### Reset the JSONL file, erasing all content

def reset_jsonl():
    with open(DATA_FILE, "w", encoding="utf-8"):
        pass

### Query the API, catch data for all cities in city_coords and save it in the JSONL file

def get_and_save_recent_all_city_data():
    reset_jsonl()
    url = "https://api.open-meteo.com/v1/forecast"
    for city, latitude, longitude in city_coords:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "timezone": "Europe/Berlin"
        }
        data = get_data(url, params)
        append_recent(data, city)
