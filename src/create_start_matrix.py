#!/usr/bin/python
import argparse
import numpy as np

def create_start_matrix(n_states = None, dist = []):
    if dist:
        start_matrix = np.array((dist))
    else:
        start_matrix = np.ones((n_states))
        start_matrix = start_matrix / n_states

    print("\n\nStart matrix created! :)\n\n%s\n\n" % start_matrix)
    return start_matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is an utility script to create the start matrix.')

    parser.add_argument('-d','--dist', help='The sequence of start distribution probability.', nargs='*', default=[])
    parser.add_argument('-ns','--nstates', help='The number of possible states.', type=int, default=0)
    args = parser.parse_args()

    create_start_matrix(int(args.nstates), map(float, args.dist))
