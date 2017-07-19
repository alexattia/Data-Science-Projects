## Face Recognition

Modern face recognition with deep learning and HOG algorithm.  

1. Find faces in image (HOG Algorithm)   
2. Affine Transformations (Face alignment using an ensemble of regression
trees)   
3. Encoding Faces (FaceNet)  
4. Make a prediction (Linear SVM)  

We are using the [Histogram of Oriented Gradients](http://lear.inrialpes.fr/people/triggs/pubs/Dalal-cvpr05.pdf) (HOG) method. Instead of computing gradients for every pixel of the image (way too much detail). We compute the weighted vote orientation  gradients of 16x16 pixels squares. Afterward, we have a simple representation (HOG image) that captures the basic structure of a face.  
All we have to do is find the part of our image that looks the most similar to a known trained HOG pattern.  
For this technique, we use the dlib Python library to generate and view HOG representations of images.  
```
face_detector = dlib.get_frontal_face_detector()
detected_faces = face_detector(image, 1)
```

After isolating the faces in our image, we need to warp (posing and projecting)the picture so the face is always in he same place. To do this, we are going to use the [face landmark estimation algorithm](http://www.csc.kth.se/~vahidk/papers/KazemiCVPR14.pdf). Following this method, there are 68 specific points (landmarks) on every face and we train a machine learning algorithm to find these 68 specific points on any face. 
```
face_pose_predictor = dlib.shape_predictor(predictor_model)
pose_landmarks = face_pose_predictor(img, f)
```
After find those landmarks, we need to use affine transformations (such as rotating, scaling and shearing --like translations) on the image so that the eyes and mouth are centered as best as possible.
```
face_aligner = openface.AlignDlib(predictor_model)
alignedFace = face_aligner.align(534, image, face_rect, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
```

The next step is encoding the detected face. For this, we use Deep Learning. We train a neural net to generate [128 measurements (face embedding)](http://www.cv-foundation.org/openaccess/content_cvpr_2015/app/1A_089.pdf) for each face.  
The training process works by looking at 3 face images at a time:  
- Load two training face images of the same known person and generate for the two pictures the 128 measurements
- Load a picture of a  different person and generate for the two pictures the 128 measurements  
Then we tweak the neural network slightly so that it makes sure the measurements for the same person are slightly closer while making sure the measurements for the two different persons are slightly further apart.
Once the network has been trained, it can generate measurements for any face, even ones it has never seen before!
```
face_encoder = dlib.face_recognition_model_v1(face_recognition_model)
face_encoding = np.array(face_encoder.compute_face_descriptor(image, pose_landmarks, 1))
```

Finally, we need a classifier (Linear SVM or other classifier) to find the person in our database of known people who has the closest measurements to our test image. We train the classifier with the measurements as input.

Thanks to Adam Geitgey who wrote a great [post](https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78) about this, I followed his pipeline.

![Result](https://github.com/alexattia/Data-Science-Projects/blob/master/FaceRecognition/result.png)