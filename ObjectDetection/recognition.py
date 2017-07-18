import cv2
from tensorflow.python.client import device_lib
from darkflow.net.build import TFNet
import numpy as np
import glob
import os

def get_available_gpus():
    """
    Return the number of GPUs availableipytho
    """
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']

def define_options(config_path):
    """
    Define the network configuration. Load the model and the weights.
    Threshold hard coded.
    :return: option for tfnet object
    """
    options = {}
    if len(get_available_gpus()) > 0 :
        options["gpu"] = 1
    else:
        options["gpu"] = 0

    model = config_path + 'cfg/yolo.cfg'
    weights = config_path + 'yolo.weights'
    if os.path.exists(model):
        options['model'] = model
    else:
        print('No cfg model')
    if os.path.exists(weights):
        options['load'] = weights
    else:
        print('No yolo weights, wget https://pjreddie.com/media/files/yolo.weights')
    options['config'] = config_path + 'cfg/'
    options["threshold"] = 0.1
    return options

def non_max_suppression_fast(boxes, probs, overlap_thresh=0.1, max_boxes=30):
    """
    Eliminating redundant object detection windows with a faster non maximum suppression method
    Greedily select high-scoring detections and skip detections that are significantly covered by 
    a previously selected detection.
    :param boxes: list of boxes 
    :param probs: list of probabilities relatives to the boxes
    """

    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    np.testing.assert_array_less(x1, x2)
    np.testing.assert_array_less(y1, y2)

    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes 
    pick = []

    # calculate the areas
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    
    # sort the bounding boxes 
    idxs = np.argsort(probs)

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the intersection
        xx1_int = np.maximum(x1[i], x1[idxs[:last]])
        yy1_int = np.maximum(y1[i], y1[idxs[:last]])
        xx2_int = np.minimum(x2[i], x2[idxs[:last]])
        yy2_int = np.minimum(y2[i], y2[idxs[:last]])
        ww_int = np.maximum(0, xx2_int - xx1_int + 0.5)
        hh_int = np.maximum(0, yy2_int - yy1_int + 0.5)
        area_int = ww_int * hh_int

        # find the union
        area_union = area[i] + area[idxs[:last]] - area_int

        # compute the ratio of overlap
        overlap = area_int / (area_union + 1e-6)

        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlap_thresh)[0])))

        if len(pick) >= max_boxes:
            break

    # return only the bounding boxes that were picked using the integer data type
    boxes = boxes[pick].astype("int")
    probs = probs[pick]
    return boxes, probs

def predict_one(image, tfnet):
    """
    Object detection in a picture
    :param image: image numpy array
    :param tfnet: net object
    :return: picture with object bounding boxes, predictions, confidence scores
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    # prediction
    result = tfnet.return_predict(image)
    # Separate each label to do non max suppresion
    for label in set([k['label'] for k in result]):
        boxes = np.array([[k['topleft']['x'], k['topleft']['y'], k['bottomright']['x'], k['bottomright']['y']] for k in result
                          if k['label'] == label])
        probs = np.array([k['confidence'] for k in result if k['label'] == label])
        # eliminating redundant object
        b, p = non_max_suppression_fast(boxes, probs)
        for k in b:
            # remove big object
            if np.abs(np.mean(np.array((k[0],k[1]))-np.array((k[2], k[3])))) < np.min(image.shape[:2])/5:
                cv2.rectangle(image, (k[0],k[1]), (k[2], k[3]), (255,0,0), 2)
                cv2.putText(image, label, (k[0],k[1]), font, 0.3, (255, 0, 0))
    return image, b, p

def predict(folder, nb_items=None, config_path='../darkflow/'):
    """
    Multiple predictions
    :param folder: folder with pictures
    :param nb_items: number of pictures to predict
    :config_path: weights and model files path
    :return: list of icture with object bounding boxes, predictions, confidence scores
    """
    images = [cv2.imread(f) for f in glob.glob(folder+'*')][:nb_items]
    results = []
    tfnet = TFNet(define_options(config_path))
    for image in images:
        results.append(predict_one(image, tfnet))
    return results

