#!/usr/bin/python
import argparse, sqlite3
import numpy as np
from utils import db
from hidden_markov import hmm
from datetime import datetime, timedelta

def create_start_matrix(n_states = None, dist = []):
    if dist:
        start_matrix = np.array((dist))
    else:
        start_matrix = np.ones((n_states))
        start_matrix = start_matrix / n_states

    print("\nStart matrix created! :)\n\n%s" % start_matrix)
    return np.asmatrix(start_matrix)
def calc_probabilities(row):
    sum = np.sum(row)
    print np.sum(row/sum)
    return row / sum

def create_trans_matrix(states_seq = [], n_states = None):
    trans_matrix = np.zeros((n_states, n_states))

    for s in range(len(states_seq)-1):
        trans_matrix[states_seq[s]-1, states_seq[s+1]-1] += 1
    trans_matrix = np.apply_along_axis( calc_probabilities, axis=1, arr=trans_matrix )
    #trans_matrix = trans_matrix / len(states_seq)

    print("\nTransition matrix created! :)\n\n%s" % trans_matrix)
    return np.asmatrix(trans_matrix)

def create_em_matrix(states_seq = [], obs_seq = [], n_states = None, n_obs = None):
    em_matrix = np.zeros((n_states, n_obs))

    for s in range(len(states_seq)-1):
        em_matrix[states_seq[s]-1, obs_seq[s]-1] += 1
    #em_matrix = em_matrix / len(obs_seq)
    em_matrix = np.apply_along_axis( calc_probabilities, axis=1, arr=em_matrix )

    print("\nEmission matrix created! :)\n\n%s" % em_matrix)
    return np.asmatrix(em_matrix)

def one_leave_out(dataset, day):
    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    cursor = conn.cursor()
    next_day = day + timedelta(days=1)
    test = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp BETWEEN ? AND ?', [day, next_day]).fetchall()
    train = cursor.execute('SELECT * FROM ' + dataset + ' WHERE timestamp < ? OR timestamp > ?', [day, next_day]).fetchall()
    return test, train

def get_possibile_states(dataset):
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
    print("\n%s possible states:\n%s\n" % (dataset, possible_states))
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

    print("\n%s possible observations:\n%s\n" % (dataset, possible_obs))

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
    print("\nObservations sequence:\n%s\n" % obs_seq)
    return obs_seq, obs_vectors

def build_states_sequence(state_rows, possible_states):
    states_list = []
    for row in state_rows:
        states_list.append(possible_states[row['activity']])
    states_seq = np.array(states_list)
    print("\nStates sequence:\n%s\n" % states_seq)
    return states_seq


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
