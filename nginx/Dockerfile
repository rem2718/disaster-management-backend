FROM tiangolo/nginx-rtmp

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install opencv-python numpy

COPY nginx.conf /etc/nginx/nginx.conf
COPY test.py /etc/nginx/test.py
COPY yolov8n-face.onnx /etc/nginx/yolov8n-face.onnx


# FROM ubuntu:latest

# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt-get update && \
#     apt-get install -y nginx && \
#     apt-get install libnginx-mod-rtmp && \
#     apt-get install libnginx-mod-stream

# COPY nginx.conf /etc/nginx/nginx.conf

# CMD ["nginx", "-g", "daemon off;"]