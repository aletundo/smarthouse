#!/usr/bin/python
import numpy as np
from random import randint
import hmm_init, sqlite3
from sklearn import metrics
from hidden_markov import hmm
from datetime import datetime, timedelta
from ..utils import db

def test_measures(correct_states, result_states, possible_states_array):

    conf_matrix = metrics.confusion_matrix(correct_states, result_states, labels = possible_states_array)
    precision = metrics.precision_score(correct_states, result_states, average = 'macro')
    recall = metrics.recall_score(correct_states, result_states, average = 'macro')
    f_measure = metrics.f1_score(correct_states, result_states, average = 'macro')

    rows_sum = np.sum(conf_matrix, axis = 1)
    diag_el = np.diag(conf_matrix)
    labels_acc = [None] * len(diag_el)

    for i in range(len(rows_sum)):
        if(rows_sum[i] != 0):
            labels_acc[i] = (diag_el[i] * 1.0) / rows_sum[i]
        else:
            labels_acc[i] = 1.0

    return f_measure, labels_acc, precision, recall, conf_matrix


#Calculate performance of input dataset using one leave out technique
def single_test(dataset, input_date):
    possible_states, possible_states_array, possible_obs, possible_obs_array = hmm_init.build_possible_structures(dataset)

    train_states_value_seq, train_states_label_seq, train_obs_seq, train_obs_vectors, test_states_value_seq, test_states_label_seq, test_obs_seq, test_obs_vectors = hmm_init.build_sets('one_leave_out', dataset, possible_states, possible_obs, input_date)

    model = hmm_init.init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq)

    viterbi_states_sequence = model.viterbi(test_obs_vectors)

    f_measure, label_acc, precision, recall, conf_matrix = test_measures(test_states_label_seq, viterbi_states_sequence, possible_states_array)

    return f_measure, precision, recall, label_acc, possible_states_array, conf_matrix

# Calculate the learning curve incrementing the training set
def learning_curve(dataset, start_day, end_day):
    start_day_train = start_day
    end_day_train = start_day + timedelta(days=1)
    f_measure_list = []

    while end_day_train <= end_day:
        possible_states, possible_states_array, possible_obs, possible_obs_array = hmm_init.build_possible_structures(dataset)

        train_states_value_seq, train_states_label_seq, train_obs_seq, train_obs_vectors, test_states_value_seq, test_states_label_seq, test_obs_seq, test_obs_vectors = hmm_init.build_sets('learning_curve', dataset, possible_states, possible_obs, start_day_train, end_day_train, end_day)

        model = hmm_init.init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq)

        viterbi_states_sequence = model.viterbi(test_obs_vectors)
        # Get only the f_measure returned value
        f_measure = test_measures(test_states_label_seq, viterbi_states_sequence, possible_states_array)[0]
        f_measure_list.append(f_measure)

        start_day_train = end_day_train
        end_day_train = end_day_train + timedelta(days=1)

    return f_measure_list

def get_obs_probability(dataset, observations, start_day, end_day):
    possible_states, possible_states_array, possible_obs, possible_obs_array = hmm_init.build_possible_structures(dataset)

    train_states_value_seq, _, train_obs_seq, _, _, _, _, _ = hmm_init.build_sets('demo', dataset, possible_states, possible_obs, start_day, end_day)

    model = hmm_init.init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq)

    return model.forward_algo(observations)

def build_random_obs(dataset):
    random_obs = []
    for i in range(5):
        random_samples = []
        for j in range(10):
            possible_obs = hmm_init.get_possible_obs(dataset + '_Sensors_Observation_Vectors')
            r = randint(1, len(possible_obs))

            sample = ''
            for k, v in possible_obs.iteritems():
                if r == v:
                    random_samples.append(k)
        random_obs.append(random_samples)
    return random_obs

def build_datasetA_obs():
    dataset_obs = []

    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    cursor = conn.cursor()

    rows = cursor.execute('SELECT * FROM OrdonezA_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2011, 11, 29, 0, 0, 59), datetime(2011, 11, 29, 0, 10, 59)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezA_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezA_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2011, 11, 29, 12, 17, 59), datetime(2011, 11, 29, 12, 27, 59)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezA_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezA_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2011, 12, 01, 11, 16, 59), datetime(2011, 12, 01, 11, 26, 59)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezA_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezA_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2011, 12, 03, 9, 0, 59), datetime(2011, 12, 03, 9, 10, 59)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezA_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezA_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2011, 12, 05, 20, 10, 59), datetime(2011, 12, 05, 20, 20, 59)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezA_Sensors_Observation_Vectors'))[1])

    return dataset_obs

def build_datasetB_obs():
    dataset_obs = []

    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    cursor = conn.cursor()

    rows = cursor.execute('SELECT * FROM OrdonezB_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2012, 11, 12, 8, 0, 0), datetime(2012, 11, 12, 8, 10, 0)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezB_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezB_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2012, 11, 13, 16, 7, 0), datetime(2012, 11, 13, 16, 17, 0)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezB_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezB_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2012, 11, 20, 15, 14, 0), datetime(2012, 11, 20, 15, 24, 0)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezB_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezB_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2012, 11, 13, 23, 17, 0), datetime(2012, 11, 23, 23, 27, 0)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezB_Sensors_Observation_Vectors'))[1])
    rows = cursor.execute('SELECT * FROM OrdonezB_Sensors_Observation_Vectors WHERE timestamp BETWEEN ? AND ? LIMIT 10', [datetime(2012, 12, 01, 23, 0, 0), datetime(2012, 12, 01, 23, 10, 0)]).fetchall()
    dataset_obs.append(hmm_init.build_obs_sequence(rows, hmm_init.get_possible_obs('OrdonezB_Sensors_Observation_Vectors'))[1])

    return dataset_obs

def build_manualA_obs():
    manual_obs = [
    ['000000000010', '000100000000', '000000000010', '000100000000', '000000000010', '000100000000', '000000000010', '000100000000', '000000000010', '000100000000'],
    ['000000000001', '000000000001', '000000000001', '000000000001', '000000000001', '000000000001', '000000000001', '000000000001', '000000000001', '000000000001'],
    ['000001000000', '100000000000', '000001000000', '100000000000', '000001000000', '100000000000', '000001000000', '100000000000', '000001000000', '100000000000'],
    ['000000000000', '000001000000', '000000000000', '000001000000', '000000000000', '000001000000', '000000000000', '000001000000', '000000000000', '000001000000'],
    ['000010000000', '000000000100', '000000000001', '100000000000', '000010000000', '000000000100', '000000000001', '100000000000', '000010000000', '000000000100'],
    ]
    return manual_obs

def build_manualB_obs():
    manual_obs = [
    ['000000000000', '000000000001', '000000000010', '000000000000', '000000000001', '000000000010', '000000000000', '000000000001', '000000000010', '000000000000'],
    ['100000000000', '100000000000', '000000100000', '000000100000', '100000000000', '100000000000', '000000100000', '000000100000', '100000000000', '100000000000'],
    ['000000100000', '000000010000', '000000100000', '000000010000', '000000100000', '000000010000', '000000100000', '000000010000', '000000100000', '000000010000'],
    ['110000000000', '000010000000' ,'110000000000', '110000000000', '000010000000' ,'110000000000', '110000000000', '000010000000' ,'110000000000', '110000000000'],
    ['010000000000', '010000000000', '010000000000', '010000000000', '010000000000', '010000000000', '010000000000', '010000000000', '010000000000', '010000000000']
    ]
    return manual_obs

def obs_probability_test(dataset, start_day, end_day):
    random_obs = build_random_obs(dataset)
    dataset_obs = build_datasetA_obs() if dataset == 'OrdonezA' else build_datasetB_obs()
    manual_obs = build_manualA_obs() if dataset == 'OrdonezA' else build_manualB_obs()
    random_results = []
    dataset_results = []
    manual_results = []
    for i in range(5):
        random_results.append(get_obs_probability(dataset, random_obs[i], start_day, end_day))
        dataset_results.append(get_obs_probability(dataset, dataset_obs[i], start_day, end_day))
        manual_results.append(get_obs_probability(dataset, manual_obs[i], start_day, end_day))
    return random_results, dataset_results, manual_results

#Calculate performance for each dataset and return average fm measure and labels accuracy
def final_test():

    initial_date_a = datetime(2011, 11, 28, 0, 0, 0)
    initial_date_b = datetime(2012, 11, 12, 0, 0, 0)

    last_date_a = datetime(2011, 12, 11, 0, 0, 0)
    last_date_b = datetime(2012, 12, 02, 0, 0, 0)

    dataset_a = 'OrdonezA'
    dataset_b = 'OrdonezB'

    f_measure_list_a = []
    f_measure_list_b = []

    precision_list_a = []
    precision_list_b = []

    recall_list_a = []
    recall_list_b = []

    labels_acc_list_a = []
    labels_acc_list_b = []

    conf_matrix_list_a = []
    conf_matrix_list_b = []

    current_date_a = initial_date_a
    current_date_b = initial_date_b

    while(current_date_a <= last_date_a):

        f_measure_a, precision_a, recall_a, labels_acc_a, labels_a, conf_matrix_a = single_test(dataset_a, current_date_a)

        f_measure_list_a.append(f_measure_a)
        precision_list_a.append(precision_a)
        recall_list_a.append(recall_a)
        labels_acc_list_a.append(labels_acc_a)
        conf_matrix_list_a.append(conf_matrix_a)

        current_date_a = current_date_a + timedelta(days = 1)

    while(current_date_b <= last_date_b):

        f_measure_b, precision_b, recall_b, labels_acc_b, labels_b, conf_matrix_b = single_test(dataset_b, current_date_b)
        f_measure_list_b.append(f_measure_b)
        precision_list_b.append(precision_b)
        recall_list_b.append(recall_b)
        labels_acc_list_b.append(labels_acc_b)
        conf_matrix_list_b.append(conf_matrix_b)

        current_date_b = current_date_b + timedelta(days = 1)

    fm_mean_a = np.mean(f_measure_list_a)
    fm_mean_b = np.mean(f_measure_list_b)

    precision_mean_a = np.mean(precision_list_a)
    precision_mean_b = np.mean(precision_list_b)

    recall_mean_a = np.mean(recall_list_a)
    recall_mean_b = np.mean(recall_list_b)


    for idx, m in enumerate(conf_matrix_list_a):
        if idx == 0:
            conf_matrix_a = m
        else:
            conf_matrix_a += m

    for idx, m in enumerate(conf_matrix_list_b):
        if idx == 0:
            conf_matrix_b = m
        else:
            conf_matrix_b+= m

    fm_std_a = np.std(f_measure_list_a)
    fm_std_b = np.std(f_measure_list_b)

    labels_matrix_a = np.matrix(labels_acc_list_a)
    labels_matrix_b = np.matrix(labels_acc_list_b)

    size_a = labels_matrix_a.shape
    size_b = labels_matrix_b.shape

    labels_accuracy_mean_a = np.sum(labels_matrix_a, axis = 0)/size_a[0]
    labels_accuracy_mean_b = np.sum(labels_matrix_b, axis = 0)/size_b[0]

    accuracy_final_list_a = []
    accuracy_final_list_b = []

    for l in range(len(labels_a)):
        accuracy_final_list_a.append((labels_a[l], labels_accuracy_mean_a[0, l]))

    for l in range(len(labels_b)):
        accuracy_final_list_b.append((labels_b[l], labels_accuracy_mean_b[0, l]))

    return fm_mean_a, fm_mean_b, fm_std_a, fm_std_b, precision_mean_a, precision_mean_b, recall_mean_a, recall_mean_b, accuracy_final_list_a, accuracy_final_list_b, conf_matrix_a, conf_matrix_b
