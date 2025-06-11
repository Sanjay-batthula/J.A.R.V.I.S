import cv2


def authenticateface():
    flag = 0
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('engine\\auth\\trainer\\trainer.yml')
    cascadepath = "engine\\auth\\haarcascade_frontalface_default.xml"
    facecascade = cv2.CascadeClassifier(cascadepath)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Update this list to match your user IDs and names
    names = ['', 'Sanjay']

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640)
    cam.set(4, 480)
    minw = 0.1 * cam.get(3)
    minh = 0.1 * cam.get(4)

    try:
        while True:
            ret, img = cam.read()
            if not ret:
                print("Failed to grab frame from camera.")
                break
            converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = facecascade.detectMultiScale(
                converted_image,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(minw), int(minh)),
            )
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                id, accuracy = recognizer.predict(converted_image[y:y+h, x:x+w])
                print(f"Recognized ID: {id} with confidence: {accuracy}")
                if accuracy < 100:
                    # Avoid IndexError if id is out of range
                    if id < len(names):
                        name = names[id]
                    else:
                        name = "unknown"
                    accuracy_text = "  {0}%".format(round(100 - accuracy))
                    flag = 1
                else:
                    name = "unknown"
                    accuracy_text = "  {0}%".format(round(100 - accuracy))
                    flag = 0
                cv2.putText(img, str(name), (x+5, y-5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, str(accuracy_text), (x+5, y+h-5), font, 1, (255, 255, 0), 1)
            cv2.imshow('camera', img)
            k = cv2.waitKey(10) & 0xff
            if k == 27:
                break
            if flag == 1:
                break
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        cam.release()
        cv2.destroyAllWindows()
    return flag