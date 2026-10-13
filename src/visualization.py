import geopandas as gpd # type: ignore
import matplotlib.pyplot as plt
from pathlib import Path
from data.map_values import city_coords, shown_cities, notation_offset
from src.data_handler import return_latest_data

BASE_DIR = Path(__file__).resolve().parent.parent

def print_country(country: str, ax):
    world = gpd.read_file(
        BASE_DIR / "data" / "country_shapes" / "ne_110m_admin_0_countries.shp"
    )
    ctry = world[world["ADMIN"] == country]

    ctry.plot(
        ax=ax,
        edgecolor="black",
        facecolor="whitesmoke"
    )
    #plt.title(country)
    
def print_city_and_temp(ax):
    for city, latitude, longitude in city_coords:
        if city not in shown_cities:
            continue
        data = return_latest_data(city)
        x_offset, y_offset = notation_offset[city]              
        temperature = data["temperature_2m"]
        ax.scatter(
            longitude,
            latitude,
            color="red",
            s=20,
            zorder=2
        )
        ax.annotate(
            f"{city}: {temperature:.1f} °C",
            xy=(longitude, latitude),
            xytext=(x_offset, y_offset),
            textcoords="offset points",
            fontsize=11,
            zorder=3
        )

def print_whole_map(country: str):
    fig, ax = plt.subplots(figsize=(8, 10))
    print_country(country, ax)
    print_city_and_temp(ax)
    ax.set_xlim(5.5, 15.5)
    ax.set_ylim(47, 55.5)
    ax.set_axis_off()
    plt.title("Aktuelle Temperaturen in Deutschland")
    plt.tight_layout()
    plt.show()