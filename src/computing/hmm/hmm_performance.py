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

    return f_measure, labels_acc

#Calculate performance of input dataset using one leave out technique
def single_test(dataset, input_date):

    possible_obs = hmm_init.get_possible_obs(dataset + '_Sensors_Observation_Vectors')
    possible_states = hmm_init.get_possibile_states(dataset + '_ADLs_Activity_States')
    test_adls, train_adls = hmm_init.one_leave_out(dataset + '_ADLs_Activity_States', input_date)
    test_sensors, train_sensors = hmm_init.one_leave_out(dataset + '_Sensors_Observation_Vectors', input_date)

    possible_states_array = sorted(possible_states, key=possible_states.get)
    possible_obs_array = sorted(possible_obs, key=possible_obs.get)

    train_states_value_seq, states_label_seq = hmm_init.build_states_sequence(train_adls, possible_states)
    train_obs_seq, train_obs_vectors = hmm_init.build_obs_sequence(train_sensors, possible_obs)

    start_matrix = hmm_init.create_start_matrix(len(possible_states))
    trans_matrix = hmm_init.create_trans_matrix(train_states_value_seq, len(possible_states))
    em_matrix = hmm_init.create_em_matrix(train_states_value_seq, train_obs_seq, len(possible_states), len(possible_obs))

    smarthouse_model = hmm(possible_states_array, possible_obs_array, start_matrix,trans_matrix,em_matrix)

    test_states_value_seq, test_states_label_seq = hmm_init.build_states_sequence(test_adls, possible_states)
    test_obs_seq, test_obs_vectors = hmm_init.build_obs_sequence(test_sensors, possible_obs)

    viterbi_states_sequence = smarthouse_model.viterbi(test_obs_vectors)

    fm_measure, label_acc = test_measures(test_states_label_seq, viterbi_states_sequence, possible_states_array)

    return fm_measure, label_acc, possible_states_array

#Calculate performance for each dataset and return average fm measure and labels accuracy
def final_test():

    initial_date_a = datetime(2011, 11, 28, 0, 0, 0)
    initial_date_b = datetime(2012, 11, 12, 0, 0, 0)

    last_date_a = datetime(2011, 12, 11, 0, 0, 0)
    last_date_b = datetime(2012, 12, 02, 0, 0, 0)

    dataset_a = 'OrdonezA'
    dataset_b = 'OrdonezB'

    fm_measure_list_a = []
    fm_measure_list_b = []

    labels_acc_list_a = []
    labels_acc_list_b = []

    current_date_a = initial_date_a
    current_date_b = initial_date_b

    while(current_date_a <= last_date_a):

        fm_measure_a, labels_acc_a, labels_a = single_test(dataset_a, current_date_a)
        fm_measure_list_a.append(fm_measure_a)
        labels_acc_list_a.append(labels_acc_a)


        current_date_a = current_date_a + timedelta(days = 1)

    while(current_date_b <= last_date_b):

        fm_measure_b, labels_acc_b, labels_b = single_test(dataset_b, current_date_b)
        fm_measure_list_b.append(fm_measure_b)
        labels_acc_list_b.append(labels_acc_b)

        current_date_b = current_date_b + timedelta(days = 1)

    fm_mean_a = sum(fm_measure_list_a) / len(fm_measure_list_a)
    fm_mean_b = sum(fm_measure_list_b) / len(fm_measure_list_b)

    labels_matrix_a = np.matrix(labels_acc_list_a)
    labels_matrix_b = np.matrix(labels_acc_list_b)

    size_a = labels_matrix_a.shape
    size_b = labels_matrix_b.shape

    label_accuracy_mean_a = np.sum(labels_matrix_a, axis = 0)/size_a[0]
    label_accuracy_mean_b = np.sum(labels_matrix_b, axis = 0)/size_b[0]

    accuracy_final_list_a = []
    accuracy_final_list_b = []

    for l in range(len(labels_a)):
        accuracy_final_list_a.append((labels_a[l], label_accuracy_mean_a[0, l]))

    for l in range(len(labels_b)):
        accuracy_final_list_b.append((labels_b[l], label_accuracy_mean_b[0, l]))

    return fm_mean_a, fm_mean_b, accuracy_final_list_a, accuracy_final_list_b
