import subprocess
import platform

class RobotRTMPClient:
    def __init__(self, name, password, link, input_cam):
        self.link = f"{link}{name}?username={name}&password={password}"
        self.input_cam = input_cam
        self.running = False
        self.process = None   
        os_name = platform.system()
        if os_name == "Windows":  
            self.f = "dshow"
        else:
            self.f = "v4l2" 

    def start_client(self):
        if self.running:
            return
        self.running = True
        command = [
            "ffmpeg",
            "-y",
            "-re",
            "-fflags",
            "nobuffer",
            "-thread_queue_size",
            "512",
            "-f",
            self.f,
            "-r",
            "30",
            "-i",
            self.input_cam,
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-tune",
            "zerolatency",
            "-f",
            "flv",
            self.link,
        ]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop_client(self):
        if not self.running:
            return
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("RTMP client stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("RTMP client forced to stop")