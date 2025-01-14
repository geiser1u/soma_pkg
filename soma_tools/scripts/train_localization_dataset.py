#!/usr/bin/python3

import os
# import sys
import numpy as np
import datetime
# import time
from sklearn import preprocessing
import pandas as pd

# tensorflow,keras by functional API
import tensorflow as tf
import tensorflow.keras
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import metrics

TREE_LOCATION_PATH = '/home/hayashi/catkin_ws/src/soma_pkg/soma_tools/data/TreeLocations_Mirais.txt'
TRAIN_X_DATASET_NAME = os.path.dirname(__file__)+'/../data/x_train-1.txt'
TRAIN_Y_DATASET_NAME = os.path.dirname(__file__)+'/../data/y_train-1.txt'

HIDDEN_N = 32
EPOCH = 2000

# model save arguments
SUFIX = '-'+os.path.splitext(os.path.basename(TRAIN_X_DATASET_NAME)
                             )[0]+'-n'+str(HIDDEN_N)+'-e'+str(EPOCH)
MODEL_NAME = os.path.dirname(
    __file__)+'/../models/model' + os.path.basename(SUFIX) + '.h5'
HISTORY_FILE_NAME = os.path.dirname(
    __file__)+'/../models/history/model'+os.path.basename(SUFIX)+'.csv'


def make_train_model(num_inputs, num_trees):
    # input layer
    inputs = tf.keras.Input(shape=(num_inputs,))
    # inputs = tf.keras.Input(shape=(1,num_inputs,))

    # hidden layer
    # num_nodes = num_trees
    num_nodes = HIDDEN_N
    dense_alpha = layers.Dense(num_nodes, activation='relu')(inputs)
    dense_beta = layers.Dense(num_nodes, activation='relu')(inputs)
    dense_gamma = layers.Dense(num_nodes, activation='relu')(inputs)

    # output layer
    output_alpha = layers.Dense(num_trees, activation='softmax')(dense_alpha)
    output_beta = layers.Dense(num_trees, activation='softmax')(dense_beta)
    output_gamma = layers.Dense(num_trees, activation='softmax')(dense_gamma)

    outputs = layers.Concatenate(name='concat', axis=1)(
        [output_alpha, output_beta, output_gamma])

    model = tf.keras.Model(inputs=inputs,
                           outputs=outputs,
                           #    outputs=[output_alpha, output_beta, output_gamma],)
                           )

    model.compile(loss=tf.keras.losses.CategoricalCrossentropy(),
                  metrics=[tf.keras.metrics.CategoricalAccuracy(),
                  tf.keras.metrics.Precision(),
                  tf.keras.metrics.Recall()],
                  optimizer=tf.keras.optimizers.Adam(),)

    return model


if __name__ == '__main__':
    print(tensorflow.__file__)

    # load tree locations
    tree_locations = np.loadtxt(TREE_LOCATION_PATH, comments='#')
    print('tree spread range =>')
    print(' x min:{},  x max:{}'.format(
        np.min(tree_locations[:, 1]),
        np.max(tree_locations[:, 1])))
    print(' y min:{},  y max:{}'.format(
        np.min(tree_locations[:, 2]),
        np.max(tree_locations[:, 2])))
    print(' Number of trees:{}'.format(len(tree_locations)))
    IDs_array = tree_locations[:, 0:1]
    IDs_array = np.ravel(IDs_array)

    print(TRAIN_X_DATASET_NAME)
    print(TRAIN_Y_DATASET_NAME)
    print(MODEL_NAME)
    # exit(1)

    _x_train = np.loadtxt(TRAIN_X_DATASET_NAME)
    print('x train shape:', _x_train.shape)

    _y_train = np.loadtxt(TRAIN_Y_DATASET_NAME)
    print('y train shape:', _y_train.shape)

    x_train = _x_train[:, 15:27]
    # x_train = np.reshape(x_train, (-1, 1, 12))
    x_train = preprocessing.minmax_scale(x_train)
    print('x_train shape:', x_train.shape)
    y_train = _y_train
    # y_train = np.reshape(_y_train, (-1, 1, 3*len(tree_locations)))
    print('y train shape:', y_train.shape)

    model = make_train_model(num_inputs=x_train.shape[1],  # input layer dimention
                             num_trees=len(tree_locations))  # output layer dimention (number of output layer nodes)
    model.summary()
    tf.keras.utils.plot_model(model,
                              show_shapes=True,
                              to_file='/home/hayashi/catkin_ws/src/soma_pkg/soma_tools/data/model.png')
    print('start training')
    history = model.fit(x=x_train,
                        y=y_train,
                        #   y=[y_train[:, 0:38], y_train[:, 38:76], y_train[:, 76:114]],
                        epochs=EPOCH,
                        verbose=1)

    # save history
    hist_df = pd.DataFrame(history.history)
    hist_df.to_csv(HISTORY_FILE_NAME)
    # save model
    dt = datetime.datetime.now()
    model.save(MODEL_NAME, save_format='h5')
