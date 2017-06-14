#!/usr/bin/python
import argparse
import numpy as np
from utils import db
from hidden_markov import hmm

def create_start_matrix(n_states = None, dist = []):
    if dist:
        start_matrix = np.array((dist))
    else:
        start_matrix = np.ones((n_states))
        start_matrix = start_matrix / n_states

    print("\nStart matrix created! :)\n\n%s" % start_matrix)
    return start_matrix

def create_trans_matrix(states_seq = [], n_states = None):
    trans_matrix = np.zeros((n_states, n_states))

    for s in range(len(states_seq)-1):
        trans_matrix[states_seq[s]-1, states_seq[s+1]-1] +=1
    trans_matrix = trans_matrix / len(states_seq)

    print("\nTransition matrix created! :)\n\n%s" % trans_matrix)
    return trans_matrix

def create_em_matrix(states_seq = [], obs_seq = [], n_states = None, n_obs = None):
    em_matrix = np.zeros((n_states, n_obs))

    for s in range(len(states_seq)-1):
        em_matrix[states_seq[s]-1, obs_seq[s]-1] +=1
    em_matrix = em_matrix / len(obs_seq)

    print("\nEmission matrix created! :)\n\n%s" % em_matrix)
    return em_matrix

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
