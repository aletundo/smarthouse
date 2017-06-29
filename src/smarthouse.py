#!/usr/bin/python
import os, numpy as np, operator
from computing.utils import txt_to_csv, db
from computing.preprocess import load_dataset, discretize_data
from computing.hmm import hmm_init, hmm_performance
from datetime import datetime, timedelta
from hidden_markov import hmm

# Change directory to the script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# txt_to_csv.convert()
# load_dataset.load()
# discretize_data.discretize_all()
#
# possible_obs = hmm_init.get_possible_obs('OrdonezB_Sensors_Observation_Vectors')
# possible_states = hmm_init.get_possibile_states('OrdonezB_ADLs_Activity_States')
# test_adls, train_adls = hmm_init.one_leave_out('OrdonezB_ADLs_Activity_States', datetime(2012, 11, 16, 0, 0, 0))
# test_sensors, train_sensors = hmm_init.one_leave_out('OrdonezB_Sensors_Observation_Vectors', datetime(2012, 11, 16, 0, 0, 0))
#
# possible_states_array = sorted(possible_states, key=possible_states.get)
# possible_obs_array = sorted(possible_obs, key=possible_obs.get)
#
# train_states_value_seq, states_label_seq = hmm_init.build_states_sequence(train_adls, possible_states)
# train_obs_seq, train_obs_vectors = hmm_init.build_obs_sequence(train_sensors, possible_obs)
#
# start_matrix = hmm_init.create_start_matrix(len(possible_states))
# trans_matrix = hmm_init.create_trans_matrix(train_states_value_seq, len(possible_states))
# em_matrix = hmm_init.create_em_matrix(train_states_value_seq, train_obs_seq, len(possible_states), len(possible_obs))
#
# smarthouse_model = hmm(possible_states_array, possible_obs_array, start_matrix,trans_matrix,em_matrix)
#
# test_states_value_seq, test_states_label_seq = hmm_init.build_states_sequence(test_adls, possible_states)
# test_obs_seq, test_obs_vectors = hmm_init.build_obs_sequence(test_sensors, possible_obs)
#
# viterbi_states_sequence = smarthouse_model.viterbi(test_obs_vectors)
#
# #print viterbi_states_sequence
# #print (hmm_performance.viterbi_accuracy(viterbi_states_sequence, test_adls))
# print hmm_performance.test_measures(test_states_label_seq, viterbi_states_sequence, possible_states_array)

def hmm_final_test(dataset, input_date):

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

    fm_measure, label_acc = hmm_performance.test_measures(test_states_label_seq, viterbi_states_sequence, possible_states_array)

    return fm_measure, label_acc, possible_states_array

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

    fm_measure_a, labels_acc_a, labels_a = hmm_final_test(dataset_a, current_date_a)
    fm_measure_list_a.append(fm_measure_a)
    labels_acc_list_a.append(labels_acc_a)


    current_date_a = current_date_a + timedelta(days = 1)

while(current_date_b <= last_date_b):

    fm_measure_b, labels_acc_b, labels_b = hmm_final_test(dataset_b, current_date_b)
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

print ("\nLabels accuracy mean OrdonezA:\n%s\n" % accuracy_final_list_a)
print ("\nLabels accuracy mean OrdonezB:\n%s\n" % accuracy_final_list_b)

print ("\nFMeasure list dataset OrdonezA:\n%s\n" % fm_measure_list_a)
print ("\nFMeasure mean dataset OrdonezA:\n%s\n" % fm_mean_a)
print ("\nFMeasure list dataset OrdonezB:\n%s\n" % fm_measure_list_b)
print ("\nFMeasure mean dataset OrdonezB:\n%s\n" % fm_mean_b)
