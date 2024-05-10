import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    FLASK_URL = os.getenv("FLASK_URL")
    RTMP_URL = os.getenv("RTMP_URL")
    SUBNET = os.getenv("SUBNET")
    CACHE_PATH = os.getenv("CACHE_PATH")
    BROKER_ADMIN_NAME = os.getenv("BROKER_ADMIN_NAME")
    BROKER_ADMIN_PASS = os.getenv("BROKER_ADMIN_PASS")
