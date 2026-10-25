import geopandas as gpd # type: ignore
import numpy as np
from shapely.geometry import Point # type: ignore

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