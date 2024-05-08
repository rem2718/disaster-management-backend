import subprocess

def run_rtmp(rtmp_link):
    command = [
        "ffmpeg",
        "-y",
        "-re",
        "-fflags", "nobuffer",
        "-thread_queue_size", "512",
        "-i", "/dev/video0",
        "-f", "v4l2"
        "-r", "30", 
        "-s", "1280x800",
        "-pix_fmt", "yuv422p",
        "-c:v", "h264",
        "-b:v", "1000k",
        "-g", "30",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-f", "flv", rtmp_link
    ]
    process = subprocess.Popen(command)

    try:
        process.wait()
    finally:
        process.terminate()
