#!/usr/bin/python
import numpy as np
import hmm_init
from sklearn import metrics
from hidden_markov import hmm
from datetime import datetime, timedelta
from ..utils import db

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

    rows_sum = np.sum(conf_matrix, axis = 1)
    diag_el = np.diag(conf_matrix)
    labels_acc = [None] * len(diag_el)

    for i in range(len(rows_sum)):
        if(rows_sum[i] != 0):
            labels_acc[i] = (diag_el[i] * 1.0) / rows_sum[i]
        else:
            labels_acc[i] = 1.0

    return f_measure, labels_acc, precision, recall, conf_matrix


#Calculate performance of input dataset using one leave out technique
def single_test(dataset, input_date):
    possible_states, possible_states_array, possible_obs, possible_obs_array = hmm_init.build_possible_structures(dataset)

    train_states_value_seq, train_states_label_seq, train_obs_seq, train_obs_vectors, test_states_value_seq, test_states_label_seq, test_obs_seq, test_obs_vectors = hmm_init.build_sets(dataset, possible_states, possible_obs, input_date)

    model = hmm_init.init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq)

    viterbi_states_sequence = model.viterbi(test_obs_vectors)

    f_measure, label_acc, precision, recall, conf_matrix = test_measures(test_states_label_seq, viterbi_states_sequence, possible_states_array)

    return f_measure, precision, recall, label_acc, possible_states_array, conf_matrix

#Calculate performance for each dataset and return average fm measure and labels accuracy
def final_test():

    initial_date_a = datetime(2011, 11, 28, 0, 0, 0)
    initial_date_b = datetime(2012, 11, 12, 0, 0, 0)

    last_date_a = datetime(2011, 12, 11, 0, 0, 0)
    last_date_b = datetime(2012, 12, 02, 0, 0, 0)

    dataset_a = 'OrdonezA'
    dataset_b = 'OrdonezB'

    f_measure_list_a = []
    f_measure_list_b = []

    precision_list_a = []
    precision_list_b = []

    recall_list_a = []
    recall_list_b = []

    labels_acc_list_a = []
    labels_acc_list_b = []

    conf_matrix_list_a = []
    conf_matrix_list_b = []

    current_date_a = initial_date_a
    current_date_b = initial_date_b

    while(current_date_a <= last_date_a):

        f_measure_a, precision_a, recall_a, labels_acc_a, labels_a, conf_matrix_a = single_test(dataset_a, current_date_a)

        f_measure_list_a.append(f_measure_a)
        precision_list_a.append(precision_a)
        recall_list_a.append(recall_a)
        labels_acc_list_a.append(labels_acc_a)
        conf_matrix_list_a.append(conf_matrix_a)

        current_date_a = current_date_a + timedelta(days = 1)

    while(current_date_b <= last_date_b):

        f_measure_b, precision_b, recall_b, labels_acc_b, labels_b, conf_matrix_b = single_test(dataset_b, current_date_b)
        f_measure_list_b.append(f_measure_b)
        precision_list_b.append(precision_b)
        recall_list_b.append(recall_b)
        labels_acc_list_b.append(labels_acc_b)
        conf_matrix_list_b.append(conf_matrix_b)

        current_date_b = current_date_b + timedelta(days = 1)

    fm_mean_a = np.mean(f_measure_list_a)
    fm_mean_b = np.mean(f_measure_list_b)

    precision_mean_a = np.mean(precision_list_a)
    precision_mean_b = np.mean(precision_list_b)

    recall_mean_a = np.mean(recall_list_a)
    recall_mean_b = np.mean(recall_list_b)


    for idx, m in enumerate(conf_matrix_list_a):
        if idx == 0:
            conf_matrices_a = m
        else:
            conf_matrices_a += m

    for idx, m in enumerate(conf_matrix_list_b):
        if idx == 0:
            conf_matrix_b = m
        else:
            conf_matrix_b+= m

    fm_std_a = np.std(f_measure_list_a)
    fm_std_b = np.std(f_measure_list_b)

    labels_matrix_a = np.matrix(labels_acc_list_a)
    labels_matrix_b = np.matrix(labels_acc_list_b)

    size_a = labels_matrix_a.shape
    size_b = labels_matrix_b.shape

    labels_accuracy_mean_a = np.sum(labels_matrix_a, axis = 0)/size_a[0]
    labels_accuracy_mean_b = np.sum(labels_matrix_b, axis = 0)/size_b[0]

    accuracy_final_list_a = []
    accuracy_final_list_b = []

    for l in range(len(labels_a)):
        accuracy_final_list_a.append((labels_a[l], labels_accuracy_mean_a[0, l]))

    for l in range(len(labels_b)):
        accuracy_final_list_b.append((labels_b[l], labels_accuracy_mean_b[0, l]))

    return fm_mean_a, fm_mean_b, fm_std_a, fm_std_b, precision_mean_a, precision_mean_b, recall_mean_a, recall_mean_b, accuracy_final_list_a, accuracy_final_list_b, conf_matrix_a, conf_matrix_b
