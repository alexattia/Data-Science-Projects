import train_keras
from keras.models import load_model
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from keras.callbacks import ModelCheckpoint
import sys

TF_CPP_MIN_LOG_LEVEL=2
TEST_BATCH = 128

def load_params():
    X_test = os.listdir('./test-jpg')
    X_test = [fn.replace('.jpg', '') for fn in X_test]
    model = load_model('model_amazon6.h5', custom_objects={'fbeta': train_keras.fbeta})
    with open('tag_columns.txt', 'r') as f:
        tag_columns = f.read().split('\n')
    return X_test, model, tag_columns

def prediction(X_test, model, tag_columns, test_folder):
    result = []
    for i in tqdm(range(0, len(X_test), TEST_BATCH)):
        X_batch = X_test[i:i+TEST_BATCH]
        X_batch = np.array([train_keras.preprocess(train_keras.load_image(fn, folder=test_folder)) for fn in X_batch])
        p = model.predict(X_batch)
        result.append(p)

    r = np.concatenate(result)
    r = r > 0.5
    table = []
    for row in r:
        t = []
        for b, v in zip(row, tag_columns):
            if b:
                t.append(v.replace('tag_', ''))
        table.append(' '.join(t))
    print('Prediction done !')
    return table

def launch(test_folder):
    X_test, model, tag_columns = load_params()
    table = prediction(X_test, model, tag_columns, test_folder)
    try:
        df_pred = pd.DataFrame.from_dict({'image_name': X_test, 'tags': table})
        df_pred.to_csv('submission9.csv', index=False)
    except:
        np.save('image_name', X_test)
        np.save('table', table)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_folder = sys.argv[1]
    else:
        test_folder='test-jpg'
    launch(test_folder)