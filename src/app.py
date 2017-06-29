#!/usr/bin/env python
# coding=utf-8
from flask import Flask, request, jsonify, render_template
import os, random, string, json, logging
from datetime import datetime
from random import randint
from computing.hmm import hmm_init
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
    if mode == 'Random':
        observations = request.form.getlist('observations[]')
        if dataset == 'OrdonezA':
            start_day = datetime.strptime(app.config['DATASET_A_START'], '%Y-%m-%d %H:%M:%S')
        else:
            start_day = datetime.strptime(app.config['DATASET_B_START'], '%Y-%m-%d %H:%M:%S')

        viterbi_states_sequence = viterbi_random(dataset, observations, start_day)
    elif mode == 'Preloaded':
        start_day = request.form['start_day']
        end_day = request.form['end_day']
        start_day = datetime.strptime(start_day, '%Y-%m-%d %H:%M:%S')
        end_day = datetime.strptime(end_day, '%Y-%m-%d %H:%M:%S')

        viterbi_states_sequence = viterbi_preloaded(dataset, start_day, end_day)

    counter = Counter(viterbi_states_sequence)
    result = dict()
    result['counter'] = dict(counter)
    result['viterbi_states_sequence'] = viterbi_states_sequence
    return jsonify(result)

def get_sensors_conf_from_db(dataset):
    conn = db.get_conn()
    conn.text_factory = str
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    sensors = cursor.execute("SELECT DISTINCT location FROM " + dataset + "_Sensors").fetchall()
    sensors = {key: value for (key, value) in enumerate(sensors)}
    return sensors

def viterbi_preloaded(dataset, start_day, end_day):
    possible_obs = hmm_init.get_possible_obs(dataset + '_Sensors_Observation_Vectors')
    possible_states = hmm_init.get_possibile_states(dataset + '_ADLs_Activity_States')

    test_adls, train_adls = hmm_init.split_dataset(dataset + '_ADLs_Activity_States', start_day, end_day)
    test_sensors, train_sensors = hmm_init.split_dataset(dataset + '_Sensors_Observation_Vectors', start_day, end_day)

    possible_states_array = sorted(possible_states, key=possible_states.get)
    possible_obs_array = sorted(possible_obs, key=possible_obs.get)

    train_states_value_seq, states_label_seq = hmm_init.build_states_sequence(train_adls, possible_states)
    train_obs_seq, train_obs_vectors = hmm_init.build_obs_sequence(train_sensors, possible_obs)

    start_matrix = hmm_init.create_start_matrix(len(possible_states))
    trans_matrix = hmm_init.create_trans_matrix(train_states_value_seq, len(possible_states))
    em_matrix = hmm_init.create_em_matrix(train_states_value_seq, train_obs_seq, len(possible_states), len(possible_obs))

    test_states_value_seq, test_states_label_seq = hmm_init.build_states_sequence(test_adls, possible_states)
    test_obs_seq, test_obs_vectors = hmm_init.build_obs_sequence(test_sensors, possible_obs)

    smarthouse_model = hmm(possible_states_array, possible_obs_array, start_matrix,trans_matrix,em_matrix)

    return smarthouse_model.viterbi(test_obs_vectors)

def viterbi_random(dataset, observations, start_day):
    possible_obs = hmm_init.get_possible_obs(dataset + '_Sensors_Observation_Vectors')
    possible_states = hmm_init.get_possibile_states(dataset + '_ADLs_Activity_States')

    test_adls, train_adls = hmm_init.one_leave_out(dataset + '_ADLs_Activity_States', start_day)
    test_sensors, train_sensors = hmm_init.one_leave_out(dataset + '_Sensors_Observation_Vectors', start_day)

    possible_states_array = sorted(possible_states, key=possible_states.get)
    possible_obs_array = sorted(possible_obs, key=possible_obs.get)

    train_states_value_seq, states_label_seq = hmm_init.build_states_sequence(train_adls, possible_states)
    train_obs_seq, train_obs_vectors = hmm_init.build_obs_sequence(train_sensors, possible_obs)

    start_matrix = hmm_init.create_start_matrix(len(possible_states))
    trans_matrix = hmm_init.create_trans_matrix(train_states_value_seq, len(possible_states))
    em_matrix = hmm_init.create_em_matrix(train_states_value_seq, train_obs_seq, len(possible_states), len(possible_obs))

    smarthouse_model = hmm(possible_states_array, possible_obs_array, start_matrix,trans_matrix,em_matrix)

    return smarthouse_model.viterbi(observations)

if __name__ == '__main__':
    app.run()
