import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    CLOUD_USER = os.getenv("CLOUD_USER")
    CLOUD_PASS = os.getenv("CLOUD_PASS")
    CLOUD_ADDRESS = os.getenv("CLOUD_ADDRESS")
    CLOUD_PORT = int(os.getenv("CLOUD_PORT"))

    LOCAL_USER = os.getenv("LOCAL_USER")
    LOCAL_PASS = os.getenv("LOCAL_PASS")
    LOCAL_ADDRESS = os.getenv("LOCAL_ADDRESS")
    LOCAL_PORT = int(os.getenv("LOCAL_PORT"))

    BUFFER_PATH = os.getenv("BUFFER_PATH")
    QUEUE_LIMIT = int(os.getenv("QUEUE_LIMIT"))
