import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    FLASK_URL = os.getenv("FLASK_URL")
    RTMP_URL = os.getenv("RTMP_URL")
    SUBNET = os.getenv("SUBNET")
    DEFAULT_TYPE = os.getenv("DEFAULT_TYPE")
