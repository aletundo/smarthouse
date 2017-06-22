#!/usr/bin/python
import numpy as np
from utils import db

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
            print row[1], viterbi_states_sequence[cont], correct
        cont = cont + 1

    accuracy = num_correct_states / len(test_adls)

    return accuracy, len(test_adls)
