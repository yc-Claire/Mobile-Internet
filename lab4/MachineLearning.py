# coding: utf-8

"""
Machine Learning Model for Predicting Advisor-Advisee Relationship.
"""

import tensorflow as tf
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Input
from keras.metrics import *
import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np
from keras.utils import np_utils
import pandas as pd
from time import time
from sklearn import metrics
from sklearn.svm import SVC

from sklearn import tree
from time import time

# prepare dataset
raw_data = open('GroundTruth_and_Features.csv', 'r')
# load the CSV file as a numpy matrix
FeatureAmount = 22
dataset = np.loadtxt(raw_data, delimiter=",")[:, :FeatureAmount + 1]
# print("dataset2: ", dataset[:5])

# separate the data from the target attributes
X = dataset[0:, 1:]
y = dataset[0:, 0]
X_train = dataset[0:-100000, 1:]

y_train = dataset[0:-100000, 0]
X_test = dataset[-100000:, 1:]
y_test = dataset[-100000:, 0]
shape_in = X_train.shape[1]  # 22
shape_out = 2
# print(X_train.shape)  # 12512 * 22
# print(X_test.shape)  # 100000 * 22


# construct Machine Learning model

def one_hot_encode_object_array(arr):
    '''One hot encode a numpy array of objects (e.g. strings)'''
    uniques, ids = np.unique(arr, return_inverse=True)
    return np_utils.to_categorical(ids, len(uniques))

# item in dataset is either [0,1] or [1,0]
y_train_ohe = one_hot_encode_object_array(y_train)
y_test_ohe = one_hot_encode_object_array(y_test)



def SVM(X_train, y_train, X_test, y_test):
    # fit a SVM model to the data
    t0 = time()
    model = SVC(kernel="rbf") # try 'rbf', originally 'linear'
    model.fit(X_train, y_train)
    print("training time:", round(time() - t0, 3), "s")
    # print(model)
    # make predictions
    t0 = time()
    expected = y_test
    predicted = model.predict(X_test)
    print("predicting time:", round(time() - t0, 3), "s")
    # summarize the fit of the model
    score = metrics.accuracy_score(expected, predicted)
    print(score)
    print(metrics.recall_score(expected, predicted))
    return model, score
    # print (data.head())


def DTree(X_train, y_train, X_test, y_test):
    model = tree.DecisionTreeClassifier(min_samples_split=40)
    t0 = time()
    model.fit(X_train, y_train)
    print("training time:", round(time() - t0, 3), "s")
    t0 = time()
    expected = y_test
    predicted = model.predict(X_test)
    print("predicting time:", round(time() - t0, 3), "s")
    # summarize the fit of the model
    score = metrics.accuracy_score(expected, predicted)
    print(score)
    print(metrics.recall_score(expected, predicted))
    return model, score


def simple_deep_learning_model(X_train, y_train, X_test, y_test, X_all, shape_in):
    model = Sequential()
    model.add(Dense(5, input_shape=(shape_in,)))  # input scale
    model.add(Activation('sigmoid'))
    # model.add(Dense(32, activation='sigmoid'))
    # model.add(Activation('sigmoid'))
    model.add(Dense(2))  # output scale
    model.add(Activation('softmax'))
    t0 = time()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=5, batch_size=5, verbose=1)
    print("training time:", round(time() - t0, 3), "s")
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print("Accuracy = {:.5f}".format(accuracy))
    print("loss = {:.5f}".format(loss))
    t0 = time()
    y_pred_test = model.predict(X_test)
    print("predicting time:", round(time() - t0, 3), "s")
    y_pred_all = model.predict(X_all)
    return model, y_pred_test, y_pred_all

print('\nML:')
model_deep_learning, y_pred, y_pred_all = simple_deep_learning_model(X_train, y_train_ohe, X_test, y_test_ohe, X,
                                                                    FeatureAmount)
print('\nSVM:')
model_SVM, score = SVM(X_train, y_train, X_test, y_test)
print('\nDTree:')
model_DTree, score2 = DTree(X_train, y_train, X_test, y_test)


def predict(model, dataset):
    file_rd = open(dataset, 'r')

    print("start loading...")
    data = np.loadtxt(file_rd, delimiter=",")[1:, :]
    print("loading finished!")

    predicted = model.predict(data)
    return predicted


def print_res(arr, output_file):
    file_wrt = open(output_file, 'w')
    for p in arr:
        file_wrt.write(str(p) + '\n')


def output_prediction(method='ML'):
    if method=='ML':
        model=model_deep_learning
    elif method=='SVM':
        model=model_SVM
    elif method=='DTree':
        model=model_DTree
    else:
        raise Exception('Illegal method!')
    predicted = predict(model, 'coauthor_feature_data.csv')
    print("\n")
    predicted_arr_num=predicted
    if method=='ML':
        print("start switching")
        predicted_arr_num = cal_set_num(predicted)
        print("switching finished!")

    print("start outputing")
    print_res(predicted_arr_num, '{}_mentor_unilateral_result_tmp.csv'.format(method))
    print("Outputing finished!")

    file_input_author = open('coauthor_feature_raw.csv', 'r')
    file_input_res = open('{}_mentor_unilateral_result_tmp.csv'.format(method), 'r')
    file_output = open('{}_MentorshipPredictionResult_IDPair2Probability.csv'.format(method), 'w')

    count = 0  # changed

    while (1):
        count += 1
        if (count % 1000000 == 0):
            print(datetime.datetime.now(), count, "MentorData")
        line1 = file_input_author.readline()
        line2 = file_input_res.readline()
        if not line1 or not line2:
            break
        line1 = line1.strip()
        line1_list = line1.split(',')
        id_i = line1_list[0]
        id_j = line1_list[1]
        res = float(line2.strip())
        file_output.write(','.join(line1_list[:2]) + ',' + str(res) + '\n')
    print("finish!")


def cal_set_num(pred_set):
    y_pred_arr_num = []
    for res in pred_set:
        y_pred_arr_num.append(res[1])
    return y_pred_arr_num

method='DTree'  # option: 'ML', 'SVM', 'DTree'
output_prediction(method)
