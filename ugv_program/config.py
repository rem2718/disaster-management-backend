import os
from dotenv import load_dotenv, set_key

load_dotenv()


def env_get(var):
    os.getenv(var)


def env_update(values):
    for var, val in values.iteritems():
        set_key(".env", var, val)
    load_dotenv()
