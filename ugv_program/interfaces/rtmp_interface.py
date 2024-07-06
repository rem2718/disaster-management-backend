import subprocess
import threading
import pickle
import os 

from facenet_pytorch import InceptionResnetV1
import torchvision.transforms as transforms
from deepface import DeepFace
import tensorflow as tf
import requests
import torch
import cv2

from model.yolo import YOLOv8_face
from config import config

torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

class RobotRTMPClient:
    def __init__(self, name, password, link, device_index):
        self.link = f"{link}{name}?username={name}&password={password}"
        self.index = device_index
        self.running = False
        self.fast = False
        self.threshold = 0.6
        self.yolov8 = YOLOv8_face("yolov8n-face.onnx")
        self.resnet = InceptionResnetV1(pretrained='casia-webface').eval()
        self.transform = transforms.Compose([
                transforms.ToPILImage(),  
                transforms.Resize((224, 224)),  
                transforms.ToTensor(),  
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  
            ])
        self._save_model()
        if self.fast:
            self.embeddings = pickle.load(open("embeddings.pkl", "rb"))
            
            
    def _login(self, username, password):
        login_url = f"{config.get('FLASK_URL')}/api/users/login"
        data = {"email_or_username": username, "password": password}
        response = requests.post(login_url, json=data)
        token = response.json().get("token")
        return token

    def _get_file(self, token):
        upload_url = f"{config.get('FLASK_URL')}/api/users/embeddings"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(upload_url, headers=headers)
        return response.content

    def _facenet_recognize(self, face):
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = cv2.resize(face, (150, 150))
        res = []
        try:
            res = DeepFace.find(
                face,
                "model",
                model_name="Facenet",
                refresh_database=False,
                silent=True,
                detector_backend="yolov8"
                )
        except Exception as e:
            pass
            
        if len(res) == 0 or len(res[0]["identity"]) == 0:
            return "Unauthorized [Unknown]"
        
        name = os.path.basename(os.path.dirname(res[0]['identity'][0]))
        return f"Authorized [{name}]"

    def _resnet_recognize(self, face):
        face = self.transform(face).unsqueeze(0)
        img_embedding = self.resnet(face)[0, :]
        min_key = float("inf")
        person = ""
        for k, v in self.embeddings.items():
            cur_key = (v - img_embedding).norm().item()
            if cur_key < min_key:
                min_key = cur_key
                person = k 
        
        if min_key >= self.threshold:
            return 'Unauthorized [Unknown]'
        return f"Authorized [{person}]"
    
    def _save_model(self):
        username, password = config.get('NAME'), config.get('PASSWORD')
        token = self._login(username, password)
        content = self._get_file(token)
        if self.fast:
            file = "model/embeddings.pkl"
        else:
            file = "model/ds_model_facenet_detector_yolov8_aligned_normalization_base_expand_0.pkl"
        with open(file, "wb") as f:
            f.write(content)   
        
    def _rtmp_process(self):
        command = [
            "ffmpeg",
            "-y",
            "-re",
            "-fflags",
            "nobuffer",
            "-thread_queue_size",
            "512",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            self.size,
            "-r",
            "30",
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "ultrafast",
            "-tune",
            "zerolatency",
            "-f",
            "flv",
            self.link,
        ]
        return subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def start_client(self):
        if self.running:
            return
        self.running = True

        self.cap = cv2.VideoCapture(self.index)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.size = f"{width}x{height}"
        if not self.cap.isOpened():
            print("Error: Could not open video device.")
            return

        def preprocessing():
            while self.running:
                _, frame = self.vdo = self.cap.retrieve()
                frame = cv2.flip(frame, 1)
                boxes, _, _, _ = self.yolov8.detect(frame)
                for box in boxes:
                    x, y, w, h = [int(coord) for coord in box]
                    face = frame[y:y+h, x:x+w]
                    if self.fast:
                        label = self._resnet_recognize(face)
                    else:
                        label = self._facenet_recognize(face)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, label, (x+5, y-10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 0, 0), 2)
                    
                self.process.stdin.write(frame.tobytes())
            self.cap.release()

        self.process = self._rtmp_process()
        self.preprocessing_thread = threading.Thread(target=preprocessing)
        self.preprocessing_thread.start()

    def stop_client(self):
        if not self.running:
            return
        self.running = False
        self.preprocessing_thread.join()
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait()
