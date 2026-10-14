import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from src.api import get_data
from data.map_values import city_coords

BASE_DIR = Path(__file__).resolve().parent.parent
RECENT_DIR = BASE_DIR / "data" / "weather_data" / "recent_values.jsonl"
ALL_DIR = BASE_DIR / "data" / "weather_data" / "all_values.jsonl"

### Append 1 line - representing data for 1 city - to recent_values.jsonl

def append_to_recent(data: dict, city: str):
    data["city"] = city
    with open(RECENT_DIR, "a", encoding="utf-8") as datei:
        datei.write(json.dumps(data, ensure_ascii=False) + "\n")

### Append only city name, retrieval timestamp, data timestamp, and data itself (temperature at 2m in °C) to all_values.jsonl

def append_to_all(data: dict, city: str): 
    retrieved_at = datetime.now(
        ZoneInfo("Europe/Berlin")
    ).isoformat(timespec="seconds")

    weather_time = datetime.fromisoformat(
        data["current"]["time"]
    ).replace(
        tzinfo=ZoneInfo(data["timezone"])
    ).isoformat(timespec="seconds")

    formatted_data = {
        "city": city, 
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "time_retrieval": retrieved_at, 
        "weather_time": weather_time, 
        "temperature_2m": data["current"]["temperature_2m"]
    }
    with open(ALL_DIR, "a", encoding="utf-8") as datei:
        datei.write(json.dumps(formatted_data, ensure_ascii=False) + "\n")

### Load recent data for given city

def load_recent_city(city: str):
    with open(RECENT_DIR, "r", encoding="utf-8") as datei:
        for zeile in datei:
            data_line = json.loads(zeile)
            if data_line["city"] == city:
                return data_line
        return {}       ### needs better handling! just there to calm down linting ###

### Reset the JSONL file, erasing all content

def reset_jsonl():
    with open(RECENT_DIR, "w", encoding="utf-8"):
        pass

### Query the API, catch data for all cities in city_coords and save it in recent_values.jsonl

def get_and_save_to_recent():
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
        append_to_recent(data, city)

### Query the API, catch data for all cities in city_coords and save parts of it in all_values.jsonl

def get_and_save_to_all():
    url = "https://api.open-meteo.com/v1/forecast"
    for city, latitude, longitude in city_coords:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "timezone": "Europe/Berlin"
        }
        data = get_data(url, params)
        append_to_all(data, city)

### Returns the latest entry for given city

def return_latest_data(city):
    latest = None
    with open(ALL_DIR, "r", encoding="utf-8") as file:
        for line in file:
            entry = json.loads(line)
            if entry["city"] != city :
                continue
            time = datetime.fromisoformat(entry["weather_time"])
            if latest is None or time > latest["weather_time"]:
                latest = {
                    **entry,
                    "weather_time":time
                }
    if latest is None:
        raise LookupError(f"No data for {city}.")
    latest["weather_time"] = latest["weather_time"].isoformat(timespec="seconds")
    return latest