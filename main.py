from src.data_handler import get_and_save_to_recent, get_and_save_to_all, load_recent_city, return_latest_data, get_and_save_recent_grid
from src.visualization import print_whole_map, print_country, test_create_country, create_grid

get_and_save_recent_grid()
print_whole_map(spacing=30000, buffer=30000)
