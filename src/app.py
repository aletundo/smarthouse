from flask import Flask, request, jsonify, render_template
import os, random, string, json, logging
from random import randint
from computing.hmm import hmm_init
from computing.utils import db

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
    r = randint(0, len(possible_obs))
    
    for k, v in possible_obs.iteritems():
        if r == v:
            sample = k

    result = dict()
    result['configuration'] = sample
    result['splitted'] = list(sample)

    return jsonify(result)


def get_sensors_conf_from_db(dataset):
    conn = db.get_conn()
    conn.text_factory = str
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    sensors = cursor.execute("SELECT DISTINCT location FROM " + dataset + "_Sensors").fetchall()
    sensors = {key: value for (key, value) in enumerate(sensors)}
    return sensors

if __name__ == '__main__':
    app.run()
