import requests # type: ignore

### Contact API at given URL and catch data for coordinates via params

def get_data(url: str, params: dict): 
    for attempt in range(3):
        try: 
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.Timeout:
            if attempt == 2:
                raise
    raise RuntimeError("API request failed after 3 attempts")