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
    conn = db.get_conn()
    conn.text_factory = str
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    sensors = cursor.execute("SELECT DISTINCT location FROM OrdonezA_Sensors").fetchall()
    #return render_template('index.html', sensors_1 = sensors[:len(sensors)/2], sensors_2 = sensors[len(sensors)/2:])
    return render_template('index.html', sensors = sensors)

@app.route('/sampling', methods=['GET'])
def random_sampling():
    dataset = request.args['dataset']
    #samples = request.args['samples'] if request.args['samples'] != '' else 10
    #rate = request.args['rate'] if request.args['rate'] != '' else 5
    possible_obs = hmm_init.get_possible_obs(dataset + '_Sensors_Observation_Vectors')
    r = randint(0, len(possible_obs))
    for k, v in possible_obs.iteritems():
        if r == v:
            sample = k
    return jsonify(list(sample))

    # for s in range(int(samples)):
    #     r = randint(0, len(possible_obs))
    #     for k, v in possible_obs.iteritems():
    #         if r == v:
    #             obs_samples.append(k)
    # return jsonify(obs_samples)

if __name__ == '__main__':
    app.run()
