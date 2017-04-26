import tensorflow as tf
import numpy as np
import cv2
import pandas as pd
import pickle
import glob

picture_size = 32   
batch_size = 128
num_steps = 30001

def load_set():
    global labels

    df = pd.DataFrame.from_csv('./train.csv')
    df.tags = df.tags.apply(lambda x:x.split(' '))
    df = pd.concat([df, df.tags.apply(pd.Series)], axis=1)
    labels = list(set(np.concatenate(df.tags)))
    mapping = dict(enumerate(labels))
    reverse_mapping = {v:k for k,v in mapping.items()}

    pictures = []
    tags = []
    for pic in np.random.choice(df.index, len(df)):
        img = cv2.imread('./train-jpg/{}.jpg'.format(pic)) / 255.
        img = cv2.resize(img, (picture_size, picture_size))
        tag = np.zeros(len(labels))
        for t in df.loc[pic].tags:
            tag[reverse_mapping[t]] = 1 
        pictures.append(img)
        tags.append(tag)

    return pictures, tags, mapping

def separate_set(pictures, labels):
    pictures_train = np.array(pictures[:int(len(pictures)*0.8)])
    labels_train = np.array(tags[:int(len(tags)*0.8)])
    print('Train shape', pictures_train.shape, labels_train.shape)

    pictures_valid = np.array(pictures[int(len(pictures)*0.8) : int(len(pictures)*0.9)])
    labels_valid = np.array(tags[int(len(tags)*0.8) : int(len(tags)*0.9)])
    print('Valid shape', pictures_valid.shape, labels_valid.shape)

    pictures_test = np.array(pictures[int(len(pictures)*0.9):])
    labels_test = np.array(tags[int(len(tags)*0.9):])
    print('Test shape', pictures_test.shape, labels_test.shape)
    return pictures_train, labels_train, pictures_valid, labels_valid, pictures_test, labels_test


def accuracy(predictions, labels):
    return (100.0 * np.sum(np.argmax(predictions, 1) == np.argmax(labels, 1))
          / predictions.shape[0])

def conv2d(x, W, stride=(1, 1), padding='SAME'):
    return tf.nn.conv2d(x, W, strides=[1, stride[0], stride[1], 1],
                      padding=padding)

def max_pool(x, ksize=(2, 2), stride=(2, 2)):
    return tf.nn.max_pool(x, ksize=[1, ksize[0], ksize[1], 1],
                        strides=[1, stride[0], stride[1], 1], padding='SAME')

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def model(data):
    # First convolution
    h_conv1 = tf.nn.relu(conv2d(data, W_1) + b_1)
    h_pool1 = max_pool(h_conv1, ksize=(2, 2), stride=(2, 2))

    # Second convolution
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_2) + b_2)
    h_pool2 = max_pool(h_conv2, ksize=(2, 2), stride=(2, 2))
    # reshape tensor into a batch of vectors
    pool_flat = tf.reshape(h_pool2, [-1, int(picture_size / 4) * int(picture_size / 4) * 64])

    # Full connected layer with 1024 neurons.
    fc = tf.nn.relu(tf.matmul(pool_flat, W_fc) + b_fc)

    # Compute logits
    return tf.matmul(fc, W_logits) + b_logits

if __name__ == "__main__":
    pictures, tags, mapping = load_set()
    pictures_train, labels_train, pictures_valid, labels_valid, pictures_test, labels_test = separate_set(pictures, tags)

    graph = tf.Graph()
    with graph.as_default():
        x = tf.placeholder(tf.float32, shape=(batch_size, picture_size, picture_size, 3))
        y_ = tf.placeholder(tf.float32, shape=(batch_size, len(labels)))
        x_valid = tf.constant(pictures_valid, dtype=tf.float32)
        x_test = tf.constant(pictures_test, dtype=tf.float32)

        # Weights and biases
        W_1 = weight_variable([3, 3, 3, 64])
        b_1 = bias_variable([32])
        W_2 = weight_variable([5, 5, 32, 128])
        b_2 = bias_variable([64])
        W_fc = weight_variable([int(picture_size / 4) * int(picture_size / 4) * 64, 1024])
        b_fc = bias_variable([1024])
        W_logits = weight_variable([1024, len(labels)])
        b_logits = bias_variable([len(labels)])

        logits = model(x)
        loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=y_))
        optimizer = tf.train.AdamOptimizer(1e-4).minimize(loss)
        y = tf.nn.softmax(logits)
        y_valid = tf.nn.softmax(model(x_valid))
        y_test = tf.nn.softmax(model(x_test))

    with tf.Session(graph = graph) as session:
        tf.global_variables_initializer().run()
        for step in range(num_steps):
            offset = (step * batch_size) % (labels_train.shape[0] - batch_size)
            batch_data = pictures_train[offset:(offset + batch_size), :, :, :]
            batch_labels = labels_train[offset:(offset + batch_size), :]
            feed_dict = {x : batch_data, y_ : batch_labels}
            _, l, predictions = session.run([optimizer, loss, y], feed_dict=feed_dict)
            if (step % 1000 == 0):
                    print('Minibatch loss at step %d: %.3f / Valid Accuracy %.2f' % (step, l, 
                                                    accuracy(y_valid.eval(), labels_valid)))
        print(accuracy(y_test.eval(), test_labels))
