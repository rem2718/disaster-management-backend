import os
from dotenv import load_dotenv, set_key

load_dotenv()


def env_get(var):
    return os.getenv(var)


def env_update(values):
    for var, val in values.items():
        set_key(".env", var, val)
    load_dotenv()
