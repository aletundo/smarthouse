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

fm_a, fm_b, labels_acc_a, labels_acc_b = hmm_performance.final_test()

print ("\nLabels accuracy mean OrdonezA:\n%s\n" % labels_acc_a)
print ("\nLabels accuracy mean OrdonezB:\n%s\n" % labels_acc_b)

print ("\nFMeasure mean dataset OrdonezA:\n%s\n" % fm_a)
print ("\nFMeasure mean dataset OrdonezB:\n%s\n" % fm_b)
