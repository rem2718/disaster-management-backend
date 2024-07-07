import pickle
import json
import os

from facenet_pytorch import InceptionResnetV1
import torchvision.transforms as transforms
from deepface import DeepFace
import requests
import torch
import cv2

from models.yolo import YOLOv8_face
from config import config

embeddings = {}
fast = False
init_image = "images/rem/rem_0.jpg"
saved_pictures = "images"
file_path = "models/embeddings.pkl"
yolov8 = YOLOv8_face("models/yolov8n-face.onnx")
model = InceptionResnetV1(pretrained='casia-webface').eval()

transform = transforms.Compose([
        transforms.ToPILImage(),  
        transforms.Resize((224, 224)),  
        transforms.ToTensor(),  
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  
    ])


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
    
        
if fast: 
    for person_folder in os.listdir(saved_pictures):
        person_path = os.path.join(saved_pictures, person_folder)
        person_embeddings = []
        
        if not os.path.isdir(person_path):
            continue
        for file in os.listdir(person_path):
            img_path = os.path.join(person_path, file)
            img = cv2.imread(img_path)
            boxes, _, _, _ = yolov8.detect(img)
            if len(boxes):
                x, y, w, h = [int(coord) for coord in boxes[0]]
                face = img[y:y+h, x:x+w]
                face = transform(face).unsqueeze(0)
                embedding = model(face)[0, :]
                person_embeddings.append(embedding)
            
        if person_embeddings:
            embeddings[person_folder] = torch.stack(person_embeddings).mean(dim=0)


        
    with open(file_path, 'wb') as f:
        pickle.dump(embeddings, f)
        
    print(f"Object saved to '{file_path}'")
    username, password = config.get('USERNAME'), config.get('PASSWORD')
    token = login(username, password)
    if upload(token, file_path):
        print("the file is uploaded.")

    
else: 
    res = DeepFace.find(
            init_image,
            "images",
            model_name="Facenet",
            silent=True,
            enforce_detection=False, 
            detector_backend="yolov8"
            )
    username, password = config.get('USERNAME'), config.get('PASSWORD')
    token = login(username, password)
    file_path = "images\\ds_model_facenet_detector_yolov8_aligned_normalization_base_expand_0.pkl"
    if upload(token, file_path):
        print("the file is uploaded.")