import tensorflow as tf
import numpy as np
import cv2
import pickle
import glob

picture_size = 28    
batch_size = 50
num_steps = 30001

def load_set():
    global M 
    pictures = []
    labels = []
    df = pd.DataFrame.from_csv('./train.csv')
    df2 = df[df.tags.isin(df['tags'].value_counts()[:15].index)]
    mapping = dict(enumerate(df2.tags.unique()))
    reverse_mapping = {v:k for k,v in mapping.items()}
    for pic in np.random.choice(df2.index, len(df2)):
        img = cv2.imread('./train-jpg/{}.jpg'.format(pic), 0) / 255.
        img = cv2.resize(img, (picture_size,picture_size))
        tag = df2.loc[pic].tags
        pictures.append(img)
        labels.append(reverse_mapping[tag])
    M = len(df.tags.unique())
    return pictures, labels, mapping

def separate_set(pictures, labels):
    pictures_train = pictures[:int(len(pictures)*0.8)]
    labels_train = labels[:int(len(pictures)*0.8)]

    pictures_valid = pictures[int(len(pictures)*0.8) : int(len(pictures)*0.9)]
    labels_valid = labels[int(len(labels)*0.8) : int(len(labels)*0.9)]

    pictures_test = pictures[int(len(pictures)*0.9):]
    labels_test = labels[int(len(labels)*0.9):]
    return pictures_train, labels_train, pictures_valid, labels_valid, pictures_test, labels_test


def reformat(dataset, labels):
    dataset = np.array(dataset).reshape((-1, picture_size, picture_size, 1)).astype(np.float32)
    labels = (np.arange(M) == np.array(labels)[:,None]).astype(np.float32).reshape(-1, M)
    print('Shape', train_dataset.shape, train_labels.shape)
    return dataset, labels

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

if __name__ = "__main__":
    pictures, labels, mapping = load_set()
    pictures_train, labels_train, pictures_valid, labels_valid, pictures_test, labels_test = separate_set(pictures, labels)
    train_dataset, train_labels = reformat(pictures_train, labels_train)
    valid_dataset, valid_labels = reformat(pictures_valid, labels_valid)
    test_dataset, test_labels = reformat(pictures_test, labels_test)

    graph = tf.Graph()

    with graph.as_default():
        x = tf.placeholder(tf.float32, shape=(batch_size, picture_size, picture_size, 1))
        y_ = tf.placeholder(tf.float32, shape=(batch_size, M))
        x_valid = tf.constant(valid_dataset, dtype=tf.float32)
        x_test = tf.constant(test_dataset, dtype=tf.float32)

        # Weights and biases
        W_1 = weight_variable([5, 5, 1, 32])
        b_1 = bias_variable([32])
        W_2 = weight_variable([5, 5, 32, 64])
        b_2 = bias_variable([64])
        W_fc = weight_variable([int(picture_size / 4) * int(picture_size / 4) * 64, 1024])
        b_fc = bias_variable([1024])
        W_logits = weight_variable([1024, M])
        b_logits = bias_variable([M])

        logits = model(x)
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y_))
        optimizer = tf.train.AdamOptimizer(1e-4).minimize(loss)
        y = tf.nn.softmax(logits)
        y_valid = tf.nn.softmax(model(x_valid))
        y_test = tf.nn.softmax(model(x_test))

    with tf.Session(graph = graph) as session:
        tf.global_variables_initializer().run()
        for step in range(num_steps):
            offset = (step * batch_size) % (train_labels.shape[0] - batch_size)
            batch_data = train_dataset[offset:(offset + batch_size), :, :, :]
            batch_labels = train_labels[offset:(offset + batch_size), :]
            feed_dict = {x : batch_data, y_ : batch_labels}
            _, l, predictions = session.run([optimizer, loss, y], feed_dict=feed_dict)
            if (step % 1000 == 0):
                    print('Minibatch loss at step %d: %.3f / Valid Accuracy %.2f' % (step, l, 
                                                    accuracy(y_valid.eval(), valid_labels))
        print(accuracy(y_test.eval(), test_labels))
