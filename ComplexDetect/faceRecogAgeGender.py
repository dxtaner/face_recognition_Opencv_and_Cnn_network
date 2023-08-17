from kisiler import *
import cv2
import numpy as np
import cvlib as cv

from keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("../training/trainer.yml")

kamera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#kamera.set(3, 1920)
#kamera.set(4, 1080)
font = cv2.FONT_HERSHEY_SIMPLEX

#kisiler verisi
kisiler=Kisiler()

gender_model = load_model("../models/gender2.h5")
age_model = load_model("../models/age3lu_2.h5")

gender_dict = {
    0:"Erkek",
    1:"Kadin"
}
age_dict = {
    0: "(0-20)",
    1: "(20-65)",
    2: "65++"
}

while kamera.isOpened():
    ret, cam = kamera.read()

    gri_toncam = cv2.cvtColor(cam,cv2.COLOR_BGR2GRAY) #yuz_tanıma
    yuz, confidence = cv.detect_face(cam)

    tonlama = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB) #yas_cinsiyet

    for idx,face in enumerate(yuz):
        #print(yuz)
        (startX, startY) = face[0], face[1]
        (endX, endY) = face[2], face[3]

        cv2.rectangle(cam, (startX, startY), (endX, endY), (0, 0, 255), 3)
        image_b = np.copy(gri_toncam[startY:endY, startX:endX])
        image_c = np.copy(tonlama[startY:endY, startX:endX])

        if (image_b.shape[0]) < 10 or (image_b.shape[1]) < 10:
            continue
        b=image_b
        
        idx,conf = recognizer.predict(b)
        if (conf<100):
            label = kisiler.isimverisiniCek(idx)
            #label = "{}:{:.2f}%".format(label, 100-conf)
        else:
            label = "bilinmeyen kisi"
            #print(idx)

        img = cv2.resize(image_c, (64, 64))
        img = img.astype("float") / 255.0
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        a = img

        conf_gender = gender_model.predict(a)[0]
        idx = np.argmax(conf_gender)
        gender = gender_dict[idx]
        gender = "{}:{:.2f}%".format(gender, conf_gender[idx] * 100)

        conf_age = age_model.predict(a)[0]
        idx = np.argmax(conf_age)
        age = age_dict[idx]
        age = "{}:{:.2f}%".format(age, conf_age[idx] * 100)

        cv2.putText(cam, gender + "/" + age, (startX + 2, startY - 40), font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(cam, label, (startX + 2, startY - 5), font, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Kamera Goruntusu", cam)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break


kamera.release()
cv2.destroyAllWindows()