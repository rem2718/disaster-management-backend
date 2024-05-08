
import json

def update_cache(data):
    try:
        with open('cache.json', 'r') as file:
            cache_data = json.load(file)
    except FileNotFoundError:
        cache_data = {}

    cache_data.update(data)

    with open('cache.json', 'w') as file:
        json.dump(cache_data, file, indent=4)
