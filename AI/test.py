import cv2


from models.yolo import YOLOv8_face

yolov8 = YOLOv8_face("models/yolov8n-face.onnx")
def test(name, password):
    rtmp_url = f'rtmp://localhost/live/{name}?username={name}&password={password}'
    cap = cv2.VideoCapture(rtmp_url)
    if not cap.isOpened():
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        boxes, _, _, _ = yolov8.detect(frame)
        for box in boxes:
            x, y, w, h = [int(coord) for coord in box]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cap.release()
    cv2.destroyAllWindows()
