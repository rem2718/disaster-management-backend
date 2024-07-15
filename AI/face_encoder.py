import os

from deepface import DeepFace
import requests

from models.yolo import YOLOv8_face
from config import config

embeddings = {}
fast = False
saved_pictures = "images"

yolov8 = YOLOv8_face("models/yolov8n-face.onnx")


def get_init_image(images_dir="images"):
    folders = [
        d for d in os.listdir(images_dir) if os.path.isdir(os.path.join(images_dir, d))
    ]
    first_folder_path = os.path.join(images_dir, folders[0])
    files = [
        f
        for f in os.listdir(first_folder_path)
        if os.path.isfile(os.path.join(first_folder_path, f))
    ]
    return os.path.join(first_folder_path, files[0])


def login(username, password):
    login_url = f"{config.get('FLASK_URL')}/api/users/login"
    data = {"email_or_username": username, "password": password}
    response = requests.post(login_url, json=data)
    token = response.json().get("token")
    return token


def upload(token, file_path):
    upload_url = f"{config.get('FLASK_URL')}/api/users/embeddings"
    headers = {
        "Authorization": f"Bearer {token}",
    }

    embeddings = open(file_path, "rb")
    response = requests.post(upload_url, files={"file": embeddings}, headers=headers)
    return response.status_code == 200


def encode():
    res = DeepFace.find(
        get_init_image(saved_pictures),
        "images",
        model_name="Facenet",
        silent=True,
        enforce_detection=False,
        detector_backend="yolov8",
    )
    username, password = config.get("USERNAME"), config.get("PASSWORD")
    token = login(username, password)
    file_path = "images\\ds_model_facenet_detector_yolov8_aligned_normalization_base_expand_0.pkl"
    if upload(token, file_path):
        print("the file is uploaded.")


encode()

import os
