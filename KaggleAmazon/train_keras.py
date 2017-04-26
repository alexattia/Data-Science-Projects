import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import glob
import matplotlib.image as mpimg
import gc

from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Lambda
from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.regularizers import l2
from keras.callbacks import ModelCheckpoint

from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

import cv2
from tqdm import tqdm

picture_size = 128
INPUT_SHAPE = (picture_size, picture_size, 4)
EPOCHS = 20
BATCH = 64
PER_EPOCH = 256

def fbeta(y_true, y_pred, threshold_shift=0):
  """
  Submissions are evaluated based on the F-beta score, it measures acccuracy using precision
  and recall. Beta = 2 here.
  """
  beta = 2

  # just in case of hipster activation at the final layer
  y_pred = K.clip(y_pred, 0, 1)

  # shifting the prediction threshold from .5 if needed
  y_pred_bin = K.round(y_pred + threshold_shift)

  tp = K.sum(K.round(y_true * y_pred_bin)) + K.epsilon()
  fp = K.sum(K.round(K.clip(y_pred_bin - y_true, 0, 1)))
  fn = K.sum(K.round(K.clip(y_true - y_pred, 0, 1)))

  precision = tp / (tp + fp)
  recall = tp / (tp + fn)

  beta_squared = beta ** 2
  return (beta_squared + 1) * (precision * recall) / (beta_squared * precision + recall + K.epsilon())

def load_image(filename, resize=True, folder='train-jpg'):
  img = mpimg.imread('./{}/{}.jpg'.format(folder, filename))
  if resize:
      img = cv2.resize(img, (picture_size, picture_size))
  return np.array(img)

# def mean_normalize(img):
#     return (img - img.mean()) / (img.max() - img.min())

def preprocess(img):
    img = img / 127.5 - 1
    return img

def generator(X, y, batch_size=32):
    X_copy, y_copy = X, y
    while True:
        for i in range(0, len(X_copy), batch_size):
            X_result, y_result = [], []
            for x, y in zip(X_copy[i:i+batch_size], y_copy[i:i+batch_size]):
                rx, ry = [load_image(x)], [y]
                rx = np.array([preprocess(x) for x in rx])
                ry = np.array(ry)
                X_result.append(rx)
                y_result.append(ry)
            X_result, y_result = np.concatenate(X_result), np.concatenate(y_result)
            yield shuffle(X_result, y_result)
        X_copy, y_copy = shuffle(X_copy, y_copy)

def create_model():
    model = Sequential()

    model.add(Conv2D(48, (8, 8), strides=(2, 2), input_shape=INPUT_SHAPE, activation='elu'))
    model.add(BatchNormalization())

    model.add(Conv2D(64, (8, 8), strides=(2, 2), activation='elu'))
    model.add(BatchNormalization())

    model.add(Conv2D(96, (5, 5), strides=(2, 2), activation='elu'))
    model.add(BatchNormalization())

    model.add(Conv2D(128, (3, 3), activation='elu'))
    model.add(BatchNormalization())

    model.add(Conv2D(128, (2, 2), activation='elu'))
    model.add(BatchNormalization())

    model.add(Flatten())
    model.add(Dropout(0.3))

    model.add(Dense(1024, activation='elu'))
    model.add(BatchNormalization())

    model.add(Dense(64, activation='elu'))
    model.add(BatchNormalization())

    model.add(Dense(n_classes, activation='sigmoid'))

        
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=[fbeta, 'accuracy']
    )

    return model

def load_set():
  global n_features, n_classes, tag_columns
  df = pd.DataFrame.from_csv('./train.csv')
  df.tags = df.tags.apply(lambda x:x.split(' '))
  df.reset_index(inplace=True)
  labels = list(df.tags)

  tags = set(np.concatenate(labels))
  tag_list = list(tags)
  tag_list.sort()
  tag_columns = ['tag_' + t for t in tag_list]
  for t in tag_list:
      df['tag_' + t] = df['tags'].map(lambda x: 1 if t in x else 0)

  X = df['image_name'].values
  y = df[tag_columns].values

  n_features = 1
  n_classes = y.shape[1]
  X, y = shuffle(X, y)

  X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.1)

  print('Train', X_train.shape, y_train.shape)
  print('Valid', X_valid.shape, y_valid.shape)
  return X_train, X_valid, y_train, y_valid

def launch():
  X_train, X_valid, y_train, y_valid = load_set()
  model = create_model()
  filepath="./weights-improvement-{epoch:02d}-{val_fbeta:.3f}.hdf5"
  checkpoint = ModelCheckpoint(filepath, monitor='val_fbeta', verbose=1, save_best_only=True, mode='max')
  callbacks_list = [checkpoint]

  history = model.fit_generator(
      generator(X_train, y_train, batch_size=BATCH),
      steps_per_epoch=PER_EPOCH,
      epochs=EPOCHS,
      validation_data=generator(X_valid, y_valid, batch_size=BATCH),
      validation_steps=len(y_valid)//(4*BATCH),
      callbacks=callbacks_list
  )
  model.save('model_amazon2.h5')

if __name__ == '__main__':
  launch()


