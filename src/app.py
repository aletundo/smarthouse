#!/usr/bin/env python
# coding=utf-8
from flask import Flask, request, jsonify, render_template
import os, random, string, json, logging
from datetime import datetime
from random import randint
from computing.hmm import hmm_init, hmm_performance
from computing.utils import db
from hidden_markov import hmm
from collections import Counter

app = Flask('smarthouse', instance_relative_config=True)
# Load the default configuration
app.config.from_object('config')

@app.route('/', methods=['GET'])
def demo():
    # Load default dataset sensors configuration
    sensors = get_sensors_conf_from_db(app.config['DATASET'])
    return render_template('index.html', sensors_1 = dict(sensors.items()[:len(sensors)/2]), sensors_2 = dict(sensors.items()[len(sensors)/2:]))

@app.route('/performance', methods=['GET'])
def performance():
    return render_template('performance.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/sensors_conf', methods=['GET'])
def get_sensors_conf():
    dataset = request.args['dataset']

    sensors = get_sensors_conf_from_db(dataset)
    return jsonify(sensors)


@app.route('/sampling', methods=['GET'])
def random_sampling():
    dataset = request.args['dataset']
    possible_obs = hmm_init.get_possible_obs(dataset + '_Sensors_Observation_Vectors')
    r = randint(1, len(possible_obs))

    sample = ''
    for k, v in possible_obs.iteritems():
        if r == v:
            sample = k

    result = dict()
    result['configuration'] = sample
    result['splitted'] = list(sample)

    return jsonify(result)

@app.route('/viterbi', methods=['POST'])
def viterbi():
    mode = request.form['mode']
    dataset = request.form['dataset']
    viterbi_states_sequence = []
    result = dict()

    if mode == 'Random':
        observations = request.form.getlist('observations[]')
        if dataset == 'OrdonezA':
            start_day = datetime.strptime(app.config['DATASET_A_START'], '%Y-%m-%d %H:%M:%S')
        else:
            start_day = datetime.strptime(app.config['DATASET_B_START'], '%Y-%m-%d %H:%M:%S')

        viterbi_states_sequence = viterbi_random(dataset, observations, start_day)
        counter = Counter(viterbi_states_sequence)
        result['counter'] = dict(counter)
        result['viterbi_states_sequence'] = viterbi_states_sequence

    elif mode == 'Preloaded':
        start_day = request.form['start_day']
        end_day = request.form['end_day']
        start_day = datetime.strptime(start_day, '%Y-%m-%d %H:%M:%S')
        end_day = datetime.strptime(end_day, '%Y-%m-%d %H:%M:%S')

        results = viterbi_preloaded(dataset, start_day, end_day)
        counter = Counter(results[0])
        result['counter'] = dict(counter)
        result['viterbi_states_sequence'] = results[0]
        result['f_measure'] = results[1]
        result['labels_accuracy'] = results[2]
        result['precision'] = results[3]
        result['recall'] = results[4]
        result['conf_matrix'] = results[5].tolist()
        result['possible_states_array'] = results[6]

    return jsonify(result)

@app.route('/forward', methods=['POST'])
def forward():
    dataset = request.form['dataset']
    observations = request.form.getlist('observations[]')
    if dataset == 'OrdonezA':
        start_day = datetime.strptime(app.config['DATASET_A_START'], '%Y-%m-%d %H:%M:%S')
    else:
        start_day = datetime.strptime(app.config['DATASET_B_START'], '%Y-%m-%d %H:%M:%S')

    possible_states, possible_states_array, possible_obs, possible_obs_array = hmm_init.build_possible_structures(dataset)
    train_states_value_seq, _, train_obs_seq, _, _, _, _, _ = hmm_init.build_sets('one_leave_out', dataset, possible_states, possible_obs, start_day)
    model = hmm_init.init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq)

    return jsonify(model.forward_algo(observations))

def get_sensors_conf_from_db(dataset):
    conn = db.get_conn()
    conn.text_factory = str
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    sensors = cursor.execute("SELECT DISTINCT location FROM " + dataset + "_Sensors").fetchall()
    sensors = {key: value for (key, value) in enumerate(sensors)}
    return sensors

def viterbi_preloaded(dataset, start_day, end_day):
    possible_states, possible_states_array, possible_obs, possible_obs_array = hmm_init.build_possible_structures(dataset)

    train_states_value_seq, train_states_label_seq, train_obs_seq, train_obs_vectors, test_states_value_seq, test_states_label_seq, test_obs_seq, test_obs_vectors = hmm_init.build_sets('demo', dataset, possible_states, possible_obs, start_day, end_day)

    model = hmm_init.init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq)

    viterbi_states_sequence = model.viterbi(test_obs_vectors)

    f_measure, labels_accuracy, precision, recall, conf_matrix = hmm_performance.test_measures(test_states_label_seq, viterbi_states_sequence, possible_states_array)

    return (viterbi_states_sequence, f_measure, labels_accuracy, precision, recall, conf_matrix, possible_states_array)

def viterbi_random(dataset, observations, start_day):
    possible_states, possible_states_array, possible_obs, possible_obs_array = hmm_init.build_possible_structures(dataset)

    train_states_value_seq, train_states_label_seq, train_obs_seq, train_obs_vectors, test_states_value_seq, test_states_label_seq, test_obs_seq, test_obs_vectors = hmm_init.build_sets('one_leave_out', dataset, possible_states, possible_obs, start_day)

    model = hmm_init.init_model(possible_states, possible_obs, possible_states_array, possible_obs_array, train_states_value_seq, train_obs_seq)

    return model.viterbi(observations)

if __name__ == '__main__':
    app.run()
