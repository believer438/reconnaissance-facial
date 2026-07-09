import cv2
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(BASE_DIR, 'dataset')

if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)

cam = cv2.VideoCapture(0)
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

id = input("Entrer ID de l'élève : ")
count = 0

while True:
    ret, img = cam.read()
    if not ret:
        print("Erreur: impossible de lire la caméra")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        cv2.imwrite(os.path.join(dataset_dir, f"User.{id}.{count}.jpg"), gray[y:y+h, x:x+w])
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow('Capture', img)

    if cv2.waitKey(100) & 0xFF == 27:
        break
    elif count >= 20:
        break

cam.release()
cv2.destroyAllWindows()
print(f"{count} images capturées pour l'élève ID {id}")
