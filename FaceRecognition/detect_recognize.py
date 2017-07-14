import dlib
from skimage import io, transform
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import glob
import openface
import pickle 
import os
import sys

from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

import face_recognition_models

face_detector = dlib.get_frontal_face_detector()
face_recognition_model = face_recognition_models.face_recognition_model_location()
face_encoder = dlib.face_recognition_model_v1(face_recognition_model)
face_pose_predictor = dlib.shape_predictor('./model/shape_predictor_68_face_landmarks.dat')

def get_detected_faces(filename):
    image = cv2.imread(filename)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image, face_detector(image, 1)

def get_face_encoding(image, detected_face):
    pose_landmarks = face_pose_predictor(image, detected_face)
    face_encoding = face_encoder.compute_face_descriptor(image, pose_landmarks, 1)
    return np.array(face_encoding)

def training(people):
    """
    We need to have only one person/face per picture
    """
    # parsing labels and reprensations
    df = pd.DataFrame()
    for p in people:
        l = []
        for filename in glob.glob('./data/%s/*' % p):
            image, face_detect = get_detected_faces(filename)
            face_encoding = get_face_encoding(image, face_detect[0])
            l.append(np.append(face_encoding, [p]))
        temp = pd.DataFrame(np.array(l))
        df = pd.concat([df, temp])
    df.reset_index(drop=True, inplace=True)

    # converting labels into int
    le = LabelEncoder()
    y = le.fit_transform(df[128])
    print("Training for {} classes.".format(len(le.classes_)))
    X = df.drop(128, axis=1)

    # training
    clf = SVC(C=1, kernel='linear', probability=True)
    clf.fit(X, y)

    # dumping model
    fName = "./classifier.pkl"
    print("Saving classifier to '{}'".format(fName))
    with open(fName, 'wb') as f:
        pickle.dump((le, clf), f)

def predict(filename):
    with open("./classifier.pkl", 'rb') as f:
        (le, clf) = pickle.load(f)
    image, detected_faces = get_detected_faces(filename)
    img = np.copy(image)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for face_detect in detected_faces:
        # draw bounding boxes
        cv2.rectangle(img, (face_detect.left(), face_detect.top()), 
                          (face_detect.right(), face_detect.bottom()), (255, 0, 0), 2)
        p = clf.predict_proba(get_face_encoding(image, face_detect).reshape(1, 128))
        if np.max(p) > 0.8:
            y_pred = le.inverse_transform(np.argmax(p))
            cv2.putText(img, y_pred, (face_detect.left(), face_detect.top()-5), font, 0.3, (255, 0, 0))
    return img

if __name__ == '__main__':
    people = os.listdir('./data/')