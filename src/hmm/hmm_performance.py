#!/usr/bin/python
import numpy as np
from sklearn import metrics
from utils import db

def viterbi_accuracy(viterbi_states_sequence, test_adls):

    conn = db.get_conn()
    cursor = conn.cursor()

    cont = 0
    correct = 0
    num_correct_states = 0.0

    for row in test_adls:
        if(row[1] == viterbi_states_sequence[cont]):
            num_correct_states = num_correct_states + 1
            correct = correct + 1
        cont = cont + 1

    accuracy = num_correct_states / len(test_adls)

    return accuracy, len(test_adls)

def test_measures(correct_states, result_states, possible_states_array):

    conf_matrix = metrics.confusion_matrix(correct_states, result_states, labels = possible_states_array)
    precision = metrics.precision_score(correct_states, result_states, average = 'macro')
    recall = metrics.recall_score(correct_states, result_states, average = 'macro')
    f_measure = metrics.f1_score(correct_states, result_states, average = 'macro')

    print "\nConfusion Matrix:\n%s\n" % conf_matrix
    print "\nPrecision:\n%s\n" % precision
    print "\nRecall:\n%s\n" % recall
    print "\nFMeasure:\n%s\n" % f_measure
