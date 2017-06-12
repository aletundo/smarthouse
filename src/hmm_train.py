import pandas as pd
import sqlite3, os, glob
import numpy as np
from hmmlearn.hmm import GaussianHMM
from os.path import basename

#Conntect to db for getting sensors observations
os.chdir(os.path.dirname(os.path.realpath(__file__)))
db_dir = '../db/'

conn = sqlite3.connect(db_dir + 'example.db')
conn.row_factory = sqlite3.Row
cursor =  conn.cursor()

#Getting sensors observations
obs_a = cursor.execute('SELECT * FROM OrdonezA_Sensors_Observation_Vectors').fetchall()

#Definition of a map to store all the configurations found in the DATASET
map = {}
key_counter = 1

for row in obs_a:
    finalrow = ''
    for col in range(len(row.keys())):
        if(col == 0):
            pass
        else:
            finalrow = finalrow + str(row[col])
    if finalrow not in map:
        map[finalrow] = key_counter
        key_counter += 1

#Define an array that contains the sequence of observations
obs_list = []
for row in obs_a:
    finalrow = ''
    for col in range(len(row.keys())):
        if(col == 0):
            pass
        else:
            finalrow = finalrow + str(row[col])
    obs_list.append(map[finalrow])

#Convert to a numpy array like
obs_array = np.array(obs_list)

#Define the HMM model
smarthouse_model = GaussianHMM(n_components=10, covariance_type="full", n_iter=100)

#Model training and result printing
smarthouse_model.fit(obs_array.reshape(-1, 1))
score = smarthouse_model.score(obs_array.reshape(-1, 1))

print('------------------------------------------------------------------------')
print("Transition matrix")
print(smarthouse_model.transmat_)
print('------------------------------------------------------------------------')
print 'Score:', score
