import json
from config import Config


def update_cache(data):
    try:
        with open(Config.CACHE_PATH, "r") as file:
            cache_data = json.load(file)
    except FileNotFoundError:
        cache_data = {}

    cache_data.update(data)

    with open(Config.CACHE_PATH, "w") as file:
        json.dump(cache_data, file, indent=4)


def read_cache():
    try:
        with open(Config.CACHE_PATH, "r") as file:
            cache_data = json.load(file)
    except FileNotFoundError:
        cache_data = {}
    return cache_data
