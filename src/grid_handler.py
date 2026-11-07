######################################################
### Responsible for handling all grid related data ###
######################################################

import geopandas as gpd # type: ignore
import numpy as np
from shapely.geometry import Point # type: ignore

import json
from pathlib import Path
from scipy.interpolate import griddata

BASE_DIR = Path(__file__).resolve().parent.parent

def create_grid(country, spacing: int = 50000, buffer: int = 50000):
    # Combines all possibly seperate areas of the countrys geometry (i.e. islands)
    country_geometry = country.geometry.union_all()

    min_x, min_y, max_x, max_y = country_geometry.bounds
    min_x, min_y = min_x - buffer, min_y - buffer
    max_x, max_y = max_x + buffer, max_y + buffer

    x_values = np.arange(min_x, max_x + spacing, spacing)
    y_values = np.arange(min_y, max_y + spacing, spacing)

    points = [
        Point(x, y)
        for x in x_values
        for y in y_values
    ]

    grid = gpd.GeoDataFrame(
        geometry=points,
        crs=country.crs
    )

    grid["inside_country"] = grid.geometry.within(
        country_geometry
    )

    return grid

### Loads existing grid data and returns it as GeoDataFrame

def prepare_grid_data():
    records = load_grid_data() 
    
    # Convert points on grid in a GeoDataFrame
    grid_data = gpd.GeoDataFrame(
        records,
        geometry=gpd.points_from_xy(
            [r["longitude"] for r in records],
            [r["latitude"] for r in records]
        ),
        crs="EPSG:4326"
    ).to_crs("EPSG:25832")

    return grid_data

### Returns the latest grid data

def load_grid_data():
    grid_path = BASE_DIR / "data" / "grid" / "grid_recent.json"
    with grid_path.open("r", encoding="utf-8") as file:
        records = json.load(file)
    return records

### Interpolates data between the original grid and returns the new data

def interpolate_grid_data(points, temperatures, grid_x, grid_y, method="cubic"):
    ### Test if the number of points (x and y coord each) is equal to number of temperature values
    if len(points) != len(temperatures):
        raise ValueError("points and temperatures must be of same size!")
    
    ### Conditions and test if temperature values are valid
    valid_values = (
        np.isfinite(temperatures)
        & (temperatures >= -60)
        & (temperatures <= 55)
    )
    if not np.any(valid_values):
        raise ValueError("No valid temperature values available!")

    ### Deleting all invalid entries

    valid_points = points[valid_values]
    valid_temps = temperatures[valid_values]

    # Interpolate temperature
    grid_temp = griddata(
        valid_points,
        valid_temps,
        (grid_x, grid_y),
        method=method
    )    
    return grid_temp