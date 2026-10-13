import geopandas as gpd # type: ignore
import matplotlib.pyplot as plt

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def print_country(country: str):
    world = gpd.read_file(
        BASE_DIR / "data" / "country_shapes" / "ne_110m_admin_0_countries.shp"
    )
    ctry = world[world["ADMIN"] == country]
    ctry.plot(
        figsize=(8, 10),
        edgecolor="black",
        facecolor="lightgray"
    )
    plt.title(country)
    plt.show()