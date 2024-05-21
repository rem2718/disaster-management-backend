import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGODB_SETTINGS = {"host": os.getenv("DB_URL")}
    MQTT_URL = os.getenv("MQTT_URL")
    MQTT_PASS = os.getenv("MQTT_PASS")
    MQTT_EMAIL = os.getenv("MQTT_EMAIL")
