import subprocess
import threading
import time

import cv2


class RobotRTMPClient:
    def __init__(self, name, password, link, device_index):
        self.link = f"{link}{name}?username={name}&password={password}"
        print(self.link)
        self.index = device_index
        self.running = False

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
            # TO-DO: fill it with your code, its just an example
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to read frame from video device.")
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                for x, y, w, h in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.process.stdin.write(frame.tobytes())
            self.cap.release()

        self.process = self._rtmp_process()
        self.preprocessing_thread = threading.Thread(target=preprocessing)
        self.preprocessing_thread.start()

    def stop_client(self):
        if not self.running:
            return
        self.running = False
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait()
        self.preprocessing_thread.join()
