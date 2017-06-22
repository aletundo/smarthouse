#!/usr/bin/python
import os
from utils import txt_to_csv, db
from preprocess import load_dataset, discretize_data
from hmm import hmm_init, hmm_performance
from datetime import datetime
from hidden_markov import hmm

# Change directory to the script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# txt_to_csv.convert()
# load_dataset.load()
# discretize_data.discretize_all()

possible_obs = hmm_init.get_possible_obs('OrdonezA_Sensors_Observation_Vectors')
possible_states = hmm_init.get_possibile_states('OrdonezA_ADLs_Activity_States')
test_adls, train_adls = hmm_init.one_leave_out('OrdonezA_ADLs_Activity_States', datetime(2011, 12, 9, 0, 0, 0))
test_sensors, train_sensors = hmm_init.one_leave_out('OrdonezA_Sensors_Observation_Vectors', datetime(2011, 12, 9, 0, 0, 0))
states_seq = hmm_init.build_states_sequence(train_adls, possible_states)
obs_seq, obs_vectors = hmm_init.build_obs_sequence(train_sensors, possible_obs)

start_matrix = hmm_init.create_start_matrix(len(possible_states))
trans_matrix = hmm_init.create_trans_matrix(states_seq, len(possible_states))
em_matrix = hmm_init.create_em_matrix(states_seq, obs_seq, len(possible_states), len(possible_obs))

smarthouse_model = hmm(possible_states.keys(),possible_obs.keys(),start_matrix,trans_matrix,em_matrix)

test_states_seq = hmm_init.build_states_sequence(test_adls, possible_states)
test_obs_seq, test_obs_vectors = hmm_init.build_obs_sequence(test_sensors, possible_obs)

viterbi_states_sequence = smarthouse_model.viterbi(test_obs_vectors)

print hmm_performance.viterbi_accuracy(viterbi_states_sequence, test_adls)
