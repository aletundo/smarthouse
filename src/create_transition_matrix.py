#!/usr/bin/python
import argparse
import numpy as np

def create_trans_matrix(states_seq, n_states):
    trans_matrix = np.zeros((n_states, n_states))

    for s in range(len(states_seq)-1):
        trans_matrix[states_seq[s]-1, states_seq[s+1]-1] +=1
    trans_matrix = trans_matrix / len(states_seq)
    
    print("\n\nTransition matrix created! :)\n\n%s\n\n" % trans_matrix)
    return trans_matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is an utility script to create the transition matrix.')

    parser.add_argument('-ss','--statesseq', help='A sequence of states separated by spaces.', nargs='*', required=True)
    parser.add_argument('-ns','--nstates', help='The number of possible states.', type=int, required=True)
    args = parser.parse_args()

    create_trans_matrix(map(int,args.statesseq), int(args.nstates))
