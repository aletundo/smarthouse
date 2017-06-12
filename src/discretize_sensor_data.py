import pandas as pd
import sqlite3, os, glob, time
from datetime import datetime, timedelta
from os.path import basename

# Change directory to the script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

db_dir = '../db/'

conn = sqlite3.connect(db_dir + 'example.db')
cursor =  conn.cursor()

def next_timeslice(timeslice, secs):
    next_slice = timeslice + timedelta(seconds=secs)
    return next_slice

# Get all tables
tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name').fetchall()

# Get all sensors table
sensors_tables = list()
for table in tables:
    if 'Sensors' in table[0]:
        sensors_tables.append(table[0])
        # Drop old tables in order to avoid issues on script re-execution
        old_sensor_table = table[0] + '_Observation_Vectors'
        cursor.execute('DROP TABLE IF EXISTS ' + old_sensor_table)

for table in sensors_tables:
    # Prepare queries to get absolute_start_time and absolute_end_time
    query_first = 'SELECT start_time FROM ' + table + ' ORDER BY start_time ASC LIMIT 1'
    query_last = 'SELECT end_time FROM ' + table + ' ORDER BY start_time DESC LIMIT 1'

    # Get absolute_start_time and absolute_end_time
    first_row = cursor.execute(query_first)
    absolute_start_time = datetime.strptime(first_row.fetchone()[0], '%Y-%m-%d %H:%M:%S')
    last_row = cursor.execute(query_last)
    absolute_end_time = datetime.strptime(last_row.fetchone()[0], '%Y-%m-%d %H:%M:%S')

    # Get available sensors
    rows = cursor.execute('SELECT DISTINCT location FROM ' + table).fetchall()
    available_sensors = ' INTEGER DEFAULT 0, '.join(str(row[0]) for row in rows)

    # Create observation vectors table
    cursor.execute('CREATE TABLE ' + table + '_Observation_Vectors (timestamp TEXT,' + available_sensors + ' INTEGER DEFAULT 0)')

    # Set the timeslice and get active sensors
    timeslice = absolute_start_time
    while (timeslice < absolute_end_time):
        query = 'SELECT location, place FROM ' + table + ' WHERE datetime(start_time) <= ? AND datetime(end_time) >= ?'
        rows = cursor.execute(query, [timeslice, timeslice]).fetchall()

        # Insert observation vector
        if len(rows) == 0:
            insert_query = 'INSERT INTO ' + table + '_Observation_Vectors(timestamp) VALUES (?)'
        else:
            active_sensors_keys = ','.join(str(row[0]) for row in rows)
            active_sensors_values = ','.join(str(1) for row in rows)
            insert_query = 'INSERT INTO ' + table + '_Observation_Vectors(timestamp,' + active_sensors_keys + ') VALUES (?,' + active_sensors_values + ')'

        string_ts = timeslice.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(insert_query, [string_ts])

        timeslice = next_timeslice(timeslice, 60)
conn.commit()
conn.close()
