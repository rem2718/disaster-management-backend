import os

import cv2

img_folder = "images"

def capture_picture():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        cv2.imshow('Capture Picture', frame)

        key = cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == 32:
            cv2.destroyAllWindows()
            return output
        elif key & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return None

def save_captured_image(frame, person_name, image_index):
    os.makedirs(f"{img_folder}/{person_name}", exist_ok=True)
    img_path = f"{img_folder}/{person_name}/{person_name}_{image_index}.jpg"
    cv2.imwrite(img_path, frame)
    return img_path

def main():
    person_name = input("Enter your name: ")

    image_index = 0
    print("Press space to capture an image, 'q' to stop capturing.")
    while True:
        frame = capture_picture()
        if frame is None:
            break
        save_captured_image(frame, person_name, image_index)
        image_index += 1

    print("The images are saved successfully!")

main()
