# coding=utf-8
#!/usr/bin/python
import argparse, sqlite3
import numpy as np
from ..utils import db
from hidden_markov import hmm
from datetime import datetime, timedelta
import sys

def create_start_matrix(n_states = None, dist = []):
    if dist:
        start_matrix = np.array((dist))
    else:
        start_matrix = np.ones((n_states))
        start_matrix = start_matrix / n_states

    #print("\nStart matrix created! :)\n\n%s" % start_matrix)
    return np.asmatrix(start_matrix)

def calc_probabilities(row):
    sum = np.sum(row)
    return row / sum

def create_trans_matrix(states_seq = [], n_states = None):

    trans_matrix = np.full((n_states, n_states), 10.0**-5)
    #trans_matrix = np.zeros((n_states, n_states))

    for s in range(len(states_seq)-1):
        trans_matrix[states_seq[s]-1, states_seq[s+1]-1] += 1

    trans_matrix = np.apply_along_axis( calc_probabilities, axis=1, arr=trans_matrix )

    #print("\nTransition matrix created! :)\n\n%s" % trans_matrix)
    return np.matrix(trans_matrix)

def create_em_matrix(states_seq = [], obs_seq = [], n_states = None, n_obs = None):
    #em_matrix = np.zeros((n_states, n_obs))
    em_matrix = np.full((n_states, n_obs), 10.0**-5)

    for s in range(len(states_seq)-1):
        em_matrix[states_seq[s]-1, obs_seq[s]-1] += 1

    em_matrix = np.apply_along_axis( calc_probabilities, axis=1, arr=em_matrix )

    #print("\nEmission matrix created! :)\n\n%s" % em_matrix)
    return np.matrix(em_matrix)

def one_leave_out_train(dataset, day):
    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    cursor = conn.cursor()
    next_day = day + timedelta(days=1)
    test = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp BETWEEN ? AND ?', [day, next_day]).fetchall()
    train = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp < ? OR timestamp > ?', [day, next_day]).fetchall()
    return test, train

def demo_train(dataset, start_day, end_day):
    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    cursor = conn.cursor()
    test = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp < ? OR timestamp > ?', [start_day, end_day]).fetchall()
    train = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp BETWEEN ? AND ?', [start_day, end_day]).fetchall()
    return test, train

def learning_curve_train(dataset, start_day, end_day, test_day):
    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    cursor = conn.cursor()
    test = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp BETWEEN ? AND ?', [test_day, test_day + timedelta(days=1)]).fetchall()
    train = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp BETWEEN ? AND ?', [start_day, end_day]).fetchall()
    return test, train

def get_possible_states(dataset):
    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    cursor = conn.cursor()

    states_rows = cursor.execute('SELECT DISTINCT activity FROM ' + dataset).fetchall()
    # Convert from tuples to list element
    states_rows = [r[0] for r in states_rows]

    possible_states = {}
    label = 1
    for s in states_rows:
        if s not in possible_states:
            possible_states[s] = label
            label += 1
    #print("\n%s possible states:\n%s\n" % (dataset, possible_states))
    return possible_states

def get_possible_obs(dataset):
    ''' The dictionary is inverted because it is used to build the observations
        sequence. So the key is a possible configuration and the value is the
        corrispective int label.
    '''

    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    observation_rows = cursor.execute('SELECT * FROM ' + dataset).fetchall()

    possible_obs = {}
    label = 1

    for row in observation_rows:
        key = ''
        for col in range(len(row.keys())):
            # Skip timestamp col
            if(col == 0):
                pass
            else:
                key = key + str(row[col])
        if key not in possible_obs:
            possible_obs[key] = label
            label += 1

    #print("\n%s possible observations:\n%s\n" % (dataset, possible_obs))

    return possible_obs

def build_obs_sequence(observation_rows, possible_obs):
    obs_list = []
    obs_vectors = []

    for row in observation_rows:
        ob_vector = ''
        for col in range(len(row.keys())):
            # Skip timestamp col
            if(col == 0):
                pass
            else:
                ob_vector = ob_vector + str(row[col])
        obs_list.append(possible_obs[ob_vector])
        obs_vectors.append(ob_vector)

    obs_seq = np.array(obs_list)
    obs_vectors = np.array(obs_vectors)

    #print("\nObservations sequence:\n%s\n" % obs_vectors)
    return obs_seq, obs_vectors

def build_states_sequence(state_rows, possible_states):
    states_value_list = []
    states_label_list = []

    for row in state_rows:
        states_value_list.append(possible_states[row['activity']])
        states_label_list.append(row['activity'])

    states_value_seq = np.array(states_value_list)
    states_label_seq = np.array(states_label_list)

    #print("\nStates sequence:\n%s\n" % states_label_seq)
    return states_value_seq, states_label_seq

def build_possible_structures(dataset):
    possible_obs = get_possible_obs(dataset + '_Sensors_Observation_Vectors')
    possible_states = get_possible_states(dataset + '_ADLs_Activity_States')
    possible_states_array = sorted(possible_states, key=possible_states.get)
    possible_obs_array = sorted(possible_obs, key=possible_obs.get)

    return possible_states, possible_states_array, possible_obs, possible_obs_array

def build_sets(mode, dataset, possible_states, possible_obs, start_day, end_day = None, test_day = None):
    if mode == 'one_leave_out':
        test_adls, train_adls = one_leave_out_train(dataset + '_ADLs_Activity_States', start_day)
        test_sensors, train_sensors = one_leave_out_train(dataset + '_Sensors_Observation_Vectors', start_day)
    elif mode == 'demo':
        test_adls, train_adls = demo_train(dataset + '_ADLs_Activity_States', start_day, end_day)
        test_sensors, train_sensors = demo_train(dataset + '_Sensors_Observation_Vectors', start_day, end_day)
    elif mode == 'learning_curve':
        test_adls, train_adls = learning_curve_train(dataset + '_ADLs_Activity_States', start_day, end_day, test_day)
        test_sensors, train_sensors = learning_curve_train(dataset + '_Sensors_Observation_Vectors', start_day, end_day, test_day)

    train_states_value_seq, train_states_label_seq = build_states_sequence(train_adls, possible_states)
    train_obs_seq, train_obs_vectors = build_obs_sequence(train_sensors, possible_obs)
    test_states_value_seq, test_states_label_seq = build_states_sequence(test_adls, possible_states)
    test_obs_seq, test_obs_vectors = build_obs_sequence(test_sensors, possible_obs)

    return train_states_value_seq, train_states_label_seq, train_obs_seq, train_obs_vectors, test_states_value_seq, test_states_label_seq, test_obs_seq, test_obs_vectors

def init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq):
    start_matrix = create_start_matrix(len(possible_states))
    trans_matrix = create_trans_matrix(train_states_value_seq, len(possible_states))
    em_matrix = create_em_matrix(train_states_value_seq, train_obs_seq, len(possible_states), len(possible_obs))

    smarthouse_model = hmm(possible_states_array, possible_obs_array, start_matrix,trans_matrix,em_matrix)

    return smarthouse_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is an utility script to create the init parameters for the HMM.\n\
    Three modes are available: \'start\', \'trans\' and \'em\'. They create respectively the start matrix, the transition \
    matrix and the emission matrix.')
    parser.add_argument('-m', '--mode', help='The mode.', choices=['start', 'trans', 'em'], required=True)
    parser.add_argument('-ss','--statesseq', help='A sequence of states separated by spaces.', nargs='*')
    parser.add_argument('-ns','--nstates', help='The number of possible states.', type=int)
    parser.add_argument('-os','--obsseq', help='A sequence of observations separated by spaces.', nargs='*')
    parser.add_argument('-no','--nobs', help='The number of possible observations.', type=int)
    parser.add_argument('-d','--dist', help='The sequence of start distribution probability.', nargs='*', default=[])
    args = parser.parse_args()

    if args.mode == 'start':
        create_start_matrix(int(args.nstates), map(float, args.dist))
    elif args.mode == 'trans':
        create_trans_matrix(map(int,args.statesseq), int(args.nstates))
    else:
        create_em_matrix(map(int, args.statesseq), map(int, args.obsseq), int(args.nstates), int(args.nobs))
