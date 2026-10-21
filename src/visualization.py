import geopandas as gpd # type: ignore
import json
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point # type: ignore
from pathlib import Path
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from data.map_values import city_coords, shown_cities, notation_offset
from src.data_handler import return_latest_data
from src.grid_handler import create_grid

BASE_DIR = Path(__file__).resolve().parent.parent

def test_create_country(country: str, transform_to_m: bool = True):
    world = gpd.read_file(
        BASE_DIR / "data" / "country_shapes" / "ne_110m_admin_0_countries.shp"
    )
    ctry = world[world["ADMIN"] == country]
    if transform_to_m:
        ctry = ctry.to_crs("EPSG:25832")
    return ctry

def print_grid_temperatures(ax):
    grid_path = BASE_DIR / "data" / "grid" / "grid_recent.jsonl"
    with grid_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    ### Only choose grid points that lie in Germany
    records = [
        record for record in records
        if record["inside_country"]
    ]

    ### Create a GDF object with points in "cartesian" coordinates and their data
    grid_data = gpd.GeoDataFrame(
        records,
        geometry=gpd.points_from_xy(
            [r["longitude"] for r in records],
            [r["latitude"] for r in records]
        ),
        crs="EPSG:4326"
    ).to_crs("EPSG:25832")

    ### Apply color spectrum representing temperature
    temperatures = grid_data["temperature_2m"]
    # Temperatures outside the given range are shown as the corresponding border
    norm = Normalize(vmin=-12, vmax=32)
    cmap = plt.get_cmap("coolwarm")

    grid_data.plot(
        ax=ax,
        color=cmap(norm(temperatures)),
        markersize=18,
        alpha=0.9,
        zorder=2
    )
    scalar_map = ScalarMappable(norm=norm, cmap=cmap)
    scalar_map.set_array([])

    plt.colorbar(
        scalar_map,
        ax=ax,
        label="Temperature °C",
        shrink=0.7
    )


def print_country(country: str, ax, transform_to_m: bool = True):
    world = gpd.read_file(
        BASE_DIR / "data" / "country_shapes" / "ne_110m_admin_0_countries.shp"
    )
    ctry = world[world["ADMIN"] == country]
    if transform_to_m:
        ctry = ctry.to_crs("EPSG:25832")
    ctry.plot(
        ax=ax,
        edgecolor="black",
        facecolor="whitesmoke"
    )
    return ctry

def print_city_and_temp(ax, transform_to_m: bool = True):
    cities_to_draw = []

    for city, latitude, longitude in city_coords:
        if city not in shown_cities:
            continue
        data = return_latest_data(city)
        cities_to_draw.append({
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "temperature": data["temperature_2m"]
        })

    points = gpd.GeoDataFrame(
        cities_to_draw,
        geometry=gpd.points_from_xy(
            [city["longitude"] for city in cities_to_draw],
            [city["latitude"] for city in cities_to_draw]
        ),
        crs="EPSG:4326"
    )

    if transform_to_m:
        points = points.to_crs("EPSG:25832")
    
    for _, city in points.iterrows():
        x = city.geometry.x
        y = city.geometry.y
        name = city["city"]
        temperature = city["temperature"]
        x_offset, y_offset = notation_offset[name]              
        ax.scatter(
            x,
            y,
            color="red",
            s=20,
            zorder=2
        )
        ax.annotate(
            f"{name}: {temperature:.1f} °C",
            xy=(x, y),
            xytext=(x_offset, y_offset),
            textcoords="offset points",
            fontsize=11,
            zorder=3
        )


def print_grid(grid, ax):
    grid[grid["inside_country"]].plot(
        ax=ax,
        color="red",
        markersize=8
    )

    grid[~grid["inside_country"]].plot(
        ax=ax,
        color="blue",
        markersize=8
    )

def print_whole_map(country: str, transform_to_m: bool = True, spacing: int = 50000, buffer: int = 50000):
    fig, ax = plt.subplots(figsize=(8, 10))
    ctry = print_country(country, ax, transform_to_m)
    #grid = create_grid(ctry, spacing, buffer)
    print_grid_temperatures(ax)
    print_city_and_temp(ax, transform_to_m)
    
    min_x, min_y, max_x, max_y = ctry.total_bounds
    if transform_to_m:
        margin = 10_000
        ax.set_aspect("equal")
    else:
        margin = 0.01
    ax.set_xlim(min_x - margin, max_x + margin)
    ax.set_ylim(min_y - margin, max_y + margin)

    ax.set_axis_off()
    plt.title("Aktuelle Temperaturen in Deutschland")
    plt.show()
