import pickle
import os
 
from facenet_pytorch import InceptionResnetV1
import torchvision.transforms as transforms
from deepface import DeepFace
import tensorflow as tf
import requests
import torch
import cv2

from models.yolo import YOLOv8_face
from config import config

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

fast = False
threshold = 0.6
yolov8 = YOLOv8_face("models/yolov8n-face.onnx")
resnet = InceptionResnetV1(pretrained='casia-webface').eval()
transform = transforms.Compose([
        transforms.ToPILImage(),  
        transforms.Resize((224, 224)),  
        transforms.ToTensor(),  
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  
    ])
with open("embeddings.pkl", "rb") as f:
    embeddings = pickle.load(f)

def login(username, password):
    login_url = f"{config.get('FLASK_URL')}/api/users/login"
    data = {"email_or_username": username, "password": password}
    response = requests.post(login_url, json=data)
    token = response.json().get("token")
    return token

def get_file(token):
    upload_url = f"{config.get('FLASK_URL')}/api/users/embeddings"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    response = requests.get(upload_url, headers=headers)
    return response.content

def facenet_recognize(face):
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face = cv2.resize(face, (150, 150))
    res = []
    try:
        res = DeepFace.find(
            face,
            "images",
            model_name="Facenet",
            refresh_database=False,
            silent=True,
            detector_backend="yolov8"
            )
    except Exception as e:
        # print(f"Error: {e}")
        pass
        
    if len(res) == 0 or len(res[0]["identity"]) == 0:
        return "Unauthorized [Unknown]"
    
    name = os.path.basename(os.path.dirname(res[0]['identity'][0]))
    return f"Authorized [{name}]"

def resnet_recognize(face):
    face = transform(face).unsqueeze(0)
    img_embedding = resnet(face)[0, :]
    min_key = float("inf")
    person = ""
    for k, v in embeddings.items():
        cur_key = (v - img_embedding).norm().item()
        if cur_key < min_key:
            min_key = cur_key
            person = k 
    # print(min_key)
    if min_key >= threshold:
        return 'Unauthorized [Unknown]'
    return f"Authorized [{person}]"
 
def save_model():
    username, password = config.get('USERNAME'), config.get('PASSWORD')
    token = login(username, password)
    content = get_file(token)
    if fast:
        file = "embeddings.pkl"
    else:
        file = "images\\ds_model_facenet_detector_yolov8_aligned_normalization_base_expand_0.pkl"
    with open(file, "wb") as f:
        f.write(content)   
        
def detect():            
    vdo = cv2.VideoCapture(0)
    while vdo.grab():
        _, frame = vdo.retrieve()
        frame = cv2.flip(frame, 1)
        boxes, _, _, _ = yolov8.detect(frame)
        for box in boxes:
            x, y, w, h = [int(coord) for coord in box]
            face = frame[y:y+h, x:x+w]
            if fast:
                label = resnet_recognize(face)
            else:
                label = facenet_recognize(face)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, label, (x+5, y-10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 0, 0), 2)
                
        cv2.imshow("output", frame)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    # save_model()
    detect()
    
