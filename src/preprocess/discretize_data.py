#!/usr/bin/python
import pandas as pd
import os, glob, time, re
from datetime import datetime, timedelta
from os.path import basename
from utils import db

def get_db():
    # Change directory to the script directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    conn = db.get_conn()
    cursor =  conn.cursor()

    return conn, cursor

def next_timeslice(timeslice, secs):
    next_slice = timeslice + timedelta(seconds=secs)
    return next_slice

def discretize_sensors():
    print ("\nDiscretizating sensors data...")

    conn, cursor =  get_db()
    # Get all tables
    tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name').fetchall()

    # Get all sensors table
    sensors_tables = list()
    for table in tables:
        if re.search('_Sensors\Z', table[0]) is not None:
            sensors_tables.append(table[0])
        # Drop old tables in order to avoid issues on script re-execution
        elif re.search('_Observation_Vectors\Z', table[0]) is not None:
            cursor.execute('DROP TABLE IF EXISTS ' + table[0])
            conn.commit()

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
        conn.commit()

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
        print("\n%s dicretized!" % table)
    conn.close()

    print ("\nSensors data discretization completed! :)")

def discretize_adls():
    print ("\nDiscretizating ADLs data...")

    conn, cursor =  get_db()
    # Get all tables
    tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name').fetchall()

    # Get all ADLs tables
    adls_tables = list()
    for table in tables:
        if re.search('_ADLs\Z', table[0]) is not None:
            adls_tables.append(table[0])
        # Drop old tables in order to avoid issues on script re-execution
        elif re.search('_Activity_States\Z', table[0]) is not None:
            cursor.execute('DROP TABLE IF EXISTS ' + table[0])
            conn.commit()

    for table in adls_tables:
        # Prepare queries to get absolute_start_time and absolute_end_time
        query_first = 'SELECT start_time FROM ' + table + ' ORDER BY start_time ASC LIMIT 1'
        query_last = 'SELECT end_time FROM ' + table + ' ORDER BY start_time DESC LIMIT 1'

        # Get absolute_start_time and absolute_end_time
        first_row = cursor.execute(query_first)
        absolute_start_time = datetime.strptime(first_row.fetchone()[0], '%Y-%m-%d %H:%M:%S')
        last_row = cursor.execute(query_last)
        absolute_end_time = datetime.strptime(last_row.fetchone()[0], '%Y-%m-%d %H:%M:%S')

        # Create activity states table
        cursor.execute('CREATE TABLE ' + table + '_Activity_States (timestamp TEXT, activity TEXT)')
        conn.commit()

        # Set the timeslice and get activities
        timeslice = absolute_start_time
        while (timeslice < absolute_end_time):
            query = 'SELECT activity FROM ' + table + ' WHERE datetime(start_time) <= ? AND datetime(end_time) >= ?'
            row = cursor.execute(query, [timeslice, timeslice]).fetchone()
            string_ts = timeslice.strftime("%Y-%m-%d %H:%M:%S")

            # Insert activity
            if row is None:
                insert_query = 'INSERT INTO ' + table + '_Activity_States(timestamp) VALUES (?)'
                cursor.execute(insert_query, [string_ts])
            else:
                insert_query = 'INSERT INTO ' + table + '_Activity_States(timestamp,activity) VALUES (?,?)'
                cursor.execute(insert_query, [string_ts, row[0]])

            timeslice = next_timeslice(timeslice, 60)
        conn.commit()
        print("\n%s dicretized!" % table)
    conn.close()

    print ("\nADLs data discretization completed! :)")

def fix_discretized_data():
    conn, cursor = get_db()
    # Get available sensors
    rows = cursor.execute('SELECT DISTINCT location FROM OrdonezA_Sensors').fetchall()
    available_sensors = ' = 0 AND '.join(str(row[0]) for row in rows)
    rows = cursor.execute('SELECT DISTINCT activity FROM OrdonezA_ADLs_Activity_States').fetchall()
    print rows

    #Delete records with label = None and zeros sensors configuration
    query_select = 'SELECT OA.timestamp FROM OrdonezA_ADLs_Activity_States AS OA JOIN OrdonezA_Sensors_Observation_Vectors AS OO\
    ON OA.timestamp = OO.timestamp WHERE OA.activity IS NULL AND ' + available_sensors + ' = 0'
    timestamps_to_delete = cursor.execute(query_select).fetchall()

    for timestamp in timestamps_to_delete:
        print timestamp[0]
        delete_adls_query = 'DELETE FROM OrdonezA_ADLs_Activity_States WHERE timestamp = ?'
        cursor.execute(delete_adls_query, [timestamp[0]])
        conn.commit()
        delete_sensors_query = 'DELETE FROM OrdonezA_Sensors_Observation_Vectors WHERE timestamp = ?'
        cursor.execute(delete_sensors_query, [timestamp[0]])
        conn.commit()

def fix_remaining_data():

    conn, cursor = get_db()

    #Select remeining records to fix where activity is null but sensor record is not null
    query_rem = 'SELECT * FROM OrdonezA_ADLs_Activity_States AS OA JOIN OrdonezA_Sensors_Observation_Vectors AS OO\
    ON OA.timestamp = OO.timestamp WHERE OA.activity IS NULL'
    rows_to_fix = cursor.execute(query_rem).fetchall()

    #For each Nonw row find the previous and the next one, compare them and try to fix the current one
    for row in rows_to_fix:

        current_timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        previous_timestamp = previous_timeslice(current_timestamp, 60)
        next_timestamp = next_timeslice(current_timestamp, 60)

        previous_row_query = 'SELECT * FROM OrdonezA_ADLs_Activity_States AS OA JOIN OrdonezA_Sensors_Observation_Vectors AS OO\
        ON OA.timestamp = OO.timestamp WHERE OA.timestamp = ?'
        next_row_query = 'SELECT * FROM OrdonezA_ADLs_Activity_States AS OA JOIN OrdonezA_Sensors_Observation_Vectors AS OO\
        ON OA.timestamp = OO.timestamp WHERE OA.timestamp = ?'

        previous_row = cursor.execute(previous_row_query, [previous_timestamp]).fetchall()
        next_row = cursor.execute(next_row_query, [next_timestamp]).fetchall()

        prev_sensors_conf = None
        curr_sensors_conf = None
        next_sensors_conf = None

        prev_label = None
        curr_label = None
        next_label = None

        #Put in a single string the sensors value of the PREVIOUS row
        for p in previous_row:
            prev_sensors_conf = str(p[3]) + str(p[4]) + str(p[5]) + str(p[6]) +\
             str(p[7]) + str(p[8]) + str(p[9]) + str(p[10])+ str(p[11])+ str(p[12])+ str(p[13])+ str(p[14])
            prev_label = p[1]

        #Put in a single string the sensors value of the CURRENT row
        curr_sensors_conf = str(row[3]) + str(row[4]) + str(row[5]) + str(row[6]) +\
         str(row[7]) + str(row[8]) + str(row[9]) + str(row[10])+ str(row[11])+ str(row[12])+ str(row[13])+ str(row[14])
        curr_label = row[1]

        #Put in a single string the sensors value of the NEXT row
        for n in next_row:
            next_sensors_conf =  str(n[3]) + str(n[4]) + str(n[5]) + str(n[6]) +\
             str(n[7]) + str(n[8]) + str(n[9]) + str(n[10])+ str(n[11])+ str(n[12])+ str(n[13])+ str(n[14])
            next_label = n[1]

        #Fix cases
        if(prev_label != None and next_label == None and prev_sensors_conf == curr_sensors_conf):
            fix_query = 'UPDATE OrdonezA_ADLs_Activity_States SET activity = ? WHERE timestamp = ?'
            row_fixed = cursor.execute(fix_query, [prev_label, row[0]])
            conn.commit()

        if(prev_label != None and next_label != None):
            if(prev_label == next_label and (prev_sensors_conf == curr_sensors_conf or curr_sensors_conf == next_sensors_conf)):

                fix_query = 'UPDATE OrdonezA_ADLs_Activity_States SET activity = ? WHERE timestamp == ?'
                row_fixed = cursor.execute(fix_query, [prev_label, row[0]])
                conn.commit()

            elif(prev_label != next_label and curr_sensors_conf == prev_sensors_conf):

                fix_query = 'UPDATE OrdonezA_ADLs_Activity_States SET activity = ? WHERE timestamp == ?'
                row_fixed = cursor.execute(fix_query, [prev_label, row[0]])
                conn.commit()

            elif(prev_label != next_label and curr_sensors_conf == next_sensors_conf):

                fix_query = 'UPDATE OrdonezA_ADLs_Activity_States SET activity = ? WHERE timestamp == ?'
                row_fixed = cursor.execute(fix_query, [next_label, row[0]])
                conn.commit()

        if(prev_label == None and next_label != None and curr_sensors_conf == next_sensors_conf):
            fix_query = 'UPDATE OrdonezA_ADLs_Activity_States SET activity = ? WHERE timestamp == ?'
            row_fixed = cursor.execute(fix_query, [next_label, row[0]])
            conn.commit()

    query_rem2 = 'SELECT OA.activity FROM OrdonezA_ADLs_Activity_States AS OA JOIN OrdonezA_Sensors_Observation_Vectors AS OO\
    ON OA.timestamp = OO.timestamp WHERE OA.activity IS NULL'
    rows_to_fix2 = cursor.execute(query_rem2).fetchall()
    for r in rows_to_fix2:
        print r


def previous_timeslice(timeslice, secs):
    previous_timeslice = timeslice - timedelta(seconds=secs)
    return previous_timeslice

def discretize_all():
    discretize_sensors()
    discretize_adls()
