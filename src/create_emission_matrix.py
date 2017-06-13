#!/usr/bin/python
import os, argparse
import numpy as np
from os.path import basename

def create_em_matrix(states_seq, obs_seq, n_states, n_obs):
    em_matrix = np.zeros((n_states, n_obs))

    for s in range(len(states_seq)-1):
        em_matrix[states_seq[s]-1, obs_seq[s]-1] +=1
    em_matrix = em_matrix / len(obs_seq)

    print("\n\nEmission matrix created! :)\n\n%s\n\n" % em_matrix)
    return em_matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is an utility script to create the transition matrix.')

    parser.add_argument('-ss','--statesseq', help='A sequence of states separated by spaces.', nargs='*', required=True)
    parser.add_argument('-ns','--nstates', help='The number of possible states.', type=int, required=True)
    parser.add_argument('-os','--obsseq', help='A sequence of observations separated by spaces.', nargs='*', required=True)
    parser.add_argument('-no','--nobs', help='The number of possible observations.', type=int, required=True)
    args = parser.parse_args()

    create_em_matrix(map(int, args.statesseq), map(int, args.obsseq), int(args.nstates), int(args.nobs))
