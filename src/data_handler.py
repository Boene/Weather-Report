import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from src.api import get_data
from data.map_values import city_coords
from src.grid_handler import create_grid
import geopandas as gpd ### notwendig? # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent
RECENT_DIR = BASE_DIR / "data" / "weather_data" / "weather_recent.jsonl"
ALL_DIR = BASE_DIR / "data" / "weather_data" / "weather_history.jsonl"
RECENT_GRID_DIR = BASE_DIR / "data" / "grid" / "grid_recent.jsonl"
ALL_GRID_DIR = BASE_DIR / "data" / "grid" / "grid_history.jsonl"

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

### Query the API, create grid, catch data for all its points and save data in grid_recent.jsonl

def get_and_save_recent_grid(country: str = "Germany"):
    url = "https://api.open-meteo.com/v1/forecast"
    batch_size = 20

    ### Create Grid
    world = gpd.read_file( ### notwendig?
        BASE_DIR / "data" / "country_shapes"
        / "ne_110m_admin_0_countries.shp"
    )
    ctry = world[world["ADMIN"] == country].to_crs("EPSG:25832")
    grid = create_grid(ctry) ### more parameters?
    
    ### Prepare Coordinates for API
    grid_api = grid.to_crs("EPSG:4326")
    latitudes = grid_api.geometry.y.tolist()
    longitudes = grid_api.geometry.x.tolist()

    records = []
    retrieved_at = datetime.now(
        ZoneInfo("Europe/Berlin")
    ).isoformat(timespec="seconds")

    for start in range(0, len(grid), batch_size):
        end = min(start + batch_size, len(grid))

        params = {
            "latitude": ",".join(
                str(x) for x in latitudes[start:end]
            ),
            "longitude": ",".join(
                str(x) for x in longitudes[start:end]
            ),
            "current": "temperature_2m",
            "timezone": "Europe/Berlin"
        }

        ### Check and process answer
        data = get_data(url, params)
        # In case of the answer only containing 1 place, its not within a list, which is necessary later on.
        if isinstance(data, dict):
            data = [data]
        if len(data) != end - start:
            raise ValueError(
                f"Erwartet: {end - start} Standorte, "
                f"erhalten: {len(data)}"
            )

        ### Save API's answer
        for offset, location_data in enumerate(data):
            index = start + offset

            records.append({
                "grid_id": index,
                "latitude": latitudes[index],
                "longitude": longitudes[index],
                "inside_country": bool(
                    grid.iloc[index]["inside_country"]
                ),
                "temperature_2m": (
                    location_data["current"]["temperature_2m"]
                ),
                "weather_time": (
                    location_data["current"]["time"]
                ),
                "retrieved_at": retrieved_at
            })

    with RECENT_GRID_DIR.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    return records


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