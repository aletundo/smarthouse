#!/usr/bin/python
import pandas as pd
import os, glob, time, re
from datetime import datetime, timedelta
from os.path import basename
from utils import db
import sqlite3
from itertools import ifilterfalse

def get_db():
    # Change directory to the script directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    conn = db.get_conn()
    cursor =  conn.cursor()

    return conn, cursor

def next_timeslice(timeslice, secs):
    next_slice = timeslice + timedelta(seconds=secs)
    return next_slice

def get_all_tables():
    conn, cursor =  get_db()
    # Get all tables
    tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name').fetchall()
    conn.close()

    return tables

def get_sensors_tables():
    tables = get_all_tables()
    # Get all sensors table
    sensors_tables = list()
    for table in tables:
        if re.search('_Sensors\Z', table[0]) is not None:
            sensors_tables.append(table[0])

    return sensors_tables

def get_adls_tables():
    tables = tables = get_all_tables()

    # Get all ADLs tables
    adls_tables = list()
    for table in tables:
        if re.search('_ADLs\Z', table[0]) is not None:
            adls_tables.append(table[0])

    return adls_tables

def discretize_sensors():
    print ("\nDiscretizating sensors data...")

    sensors_tables = get_sensors_tables()
    adls_tables = get_adls_tables()
    conn, cursor =  get_db()

    for index, table in enumerate(sensors_tables):
        # Prepare queries to get absolute_start_time and absolute_end_time
        query_first = 'SELECT start_time FROM ' + adls_tables[index] + ' ORDER BY start_time ASC LIMIT 1'
        query_last = 'SELECT end_time FROM ' + adls_tables[index] + ' ORDER BY start_time DESC LIMIT 1'

        # Get absolute_start_time and absolute_end_time
        first_row = cursor.execute(query_first)
        absolute_start_time = datetime.strptime(first_row.fetchone()[0], '%Y-%m-%d %H:%M:%S')
        last_row = cursor.execute(query_last)
        absolute_end_time = datetime.strptime(last_row.fetchone()[0], '%Y-%m-%d %H:%M:%S')

        # Get available sensors
        rows = cursor.execute('SELECT DISTINCT location FROM ' + table).fetchall()
        available_sensors = ' INTEGER DEFAULT 0, '.join(str(row[0]) for row in rows)

        # Create observation vectors table
        cursor.execute('DROP TABLE IF EXISTS ' + table + '_Observation_Vectors')
        conn.commit()
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
        print("\n%s discretized!" % table)
    conn.close()

    print ("\nSensors data discretization completed! :)")

def discretize_adls():
    print ("\nDiscretizating ADLs data...")

    adls_tables = get_adls_tables()
    conn, cursor =  get_db()

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
        cursor.execute('DROP TABLE IF EXISTS ' + table + '_Activity_States')
        conn.commit()
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
        print("\n%s discretized!" % table)
    conn.close()
    print ("\nADLs data discretization completed! :)")

def remove_useless_data():
    print("\nRemoving useless data...")
    conn, cursor = get_db()

    sensors_tables = get_sensors_tables()
    adls_tables = get_adls_tables()

    # Sensors and ADLs tables are sorted by their name.
    # So it is sure we can use index to get the corresponding ADLs dataset table
    # iterating only on sensors tables.
    # We can avoid regex using this strategy.

    # Delete records with label = None and zeros sensors configuration.
    for index, table in enumerate(sensors_tables):
        # Get available sensors
        rows = cursor.execute('SELECT DISTINCT location FROM ' + table).fetchall()
        available_sensors = ' = 0 AND '.join(str(row[0]) for row in rows)

        query_select = 'SELECT OA.timestamp FROM ' + adls_tables[index] +'_Activity_States AS OA JOIN ' + table + '_Observation_Vectors AS OO\
        ON OA.timestamp = OO.timestamp WHERE OA.activity IS NULL AND ' + available_sensors + ' = 0'
        timestamps_to_delete = cursor.execute(query_select).fetchall()

        for timestamp in timestamps_to_delete:
            delete_adls_query = 'DELETE FROM ' + adls_tables[index] + '_Activity_States WHERE timestamp = ?'
            cursor.execute(delete_adls_query, [timestamp[0]])
            conn.commit()
            delete_sensors_query = 'DELETE FROM ' + table + '_Observation_Vectors WHERE timestamp = ?'
            cursor.execute(delete_sensors_query, [timestamp[0]])
            conn.commit()

    # Delete sensors data which exceed the latest adls timestamp available
    for index, table, in enumerate(adls_tables):
        latest_timestamp = cursor.execute('SELECT timestamp FROM ' + table + '_Activity_States ORDER BY timestamp DESC LIMIT 1').fetchone()
        cursor.execute('DELETE FROM ' + sensors_tables[index] + '_Observation_Vectors WHERE timestamp > ?', [latest_timestamp[0]])
        conn.commit()

    conn.close()
    print("\nRemoval completed! :)")

def fix_remaining_data():

    #conn, cursor = get_db()
    conn = db.get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    adls_tables = get_adls_tables()
    sensors_tables = get_sensors_tables()
    for index, table in enumerate(adls_tables):

        #Select remeining records to fix where activity is null but sensor record is not null
        query_rem = 'SELECT * FROM ' + table + '_Activity_States AS OA JOIN ' + sensors_tables[index] + '_Observation_Vectors AS OO\
        ON OA.timestamp = OO.timestamp WHERE OA.activity IS NULL'
        rows_to_fix = cursor.execute(query_rem).fetchall()

        number_of_row_none = 'SELECT COUNT(*) FROM ' + table + '_Activity_States AS OA JOIN ' + sensors_tables[index] + '_Observation_Vectors AS OO\
        ON OA.timestamp = OO.timestamp WHERE OA.activity IS NULL'
        num_rows_not_fixed = cursor.execute(number_of_row_none).fetchall()

        num_of_rem_rows = num_rows_not_fixed
        fix_again = True

        while (fix_again):
            fixed_elements = []
            num_rows_not_fixed = num_of_rem_rows

            #For each Nonw row find the previous and the next one, compare them and try to fix the current one
            for row in rows_to_fix:

                current_timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                previous_timestamp = next_timeslice(current_timestamp, -60)
                next_timestamp = next_timeslice(current_timestamp, 60)

                previous_row_query = 'SELECT * FROM ' + table + '_Activity_States AS OA JOIN ' + sensors_tables[index] + '_Observation_Vectors AS OO\
                ON OA.timestamp = OO.timestamp WHERE OA.timestamp = ?'
                next_row_query = 'SELECT * FROM ' + table + '_Activity_States AS OA JOIN ' + sensors_tables[index] + '_Observation_Vectors AS OO\
                ON OA.timestamp = OO.timestamp WHERE OA.timestamp = ?'

                previous_row = cursor.execute(previous_row_query, [previous_timestamp]).fetchall()
                next_row = cursor.execute(next_row_query, [next_timestamp]).fetchall()

                #Get rows label and put the sensors config in a single string
                prev_sensors_conf = ''
                curr_sensors_conf = ''
                next_sensors_conf = ''

                prev_label = ''
                curr_label = ''
                next_label = ''

                for col in range(len(row.keys())):
                    # Skip timestamps cols or get rows label
                    if(col < 3):
                        if(col == 1):

                            for p in previous_row:
                                prev_label = p[1]
                            for n in next_row:
                                next_label = n[1]
                            curr_label = row[1]

                        else:
                            pass

                    else:
                        for p in previous_row:
                            prev_sensors_conf = prev_sensors_conf + str(p[col])
                        for n in next_row:
                            next_sensors_conf = next_sensors_conf + str(n[col])
                        curr_sensors_conf = curr_sensors_conf + str(row[col])

                #Fix cases
                if(prev_label != None and next_label == None and prev_sensors_conf == curr_sensors_conf):
                    fix_query = 'UPDATE ' + table + '_Activity_States SET activity = ? WHERE timestamp = ?'
                    row_fixed = cursor.execute(fix_query, [prev_label, row[0]])
                    conn.commit()
                    fixed_elements.append(row)

                if(prev_label != None and next_label != None):
                    if(prev_label == next_label and (prev_sensors_conf == curr_sensors_conf or curr_sensors_conf == next_sensors_conf)):

                        fix_query = 'UPDATE ' + table + '_Activity_States SET activity = ? WHERE timestamp = ?'
                        row_fixed = cursor.execute(fix_query, [prev_label, row[0]])
                        conn.commit()
                        fixed_elements.append(row)

                    elif(prev_label != next_label and curr_sensors_conf == prev_sensors_conf):

                        fix_query = 'UPDATE ' + table + '_Activity_States SET activity = ? WHERE timestamp = ?'
                        row_fixed = cursor.execute(fix_query, [prev_label, row[0]])
                        conn.commit()
                        fixed_elements.append(row)

                    elif(prev_label != next_label and curr_sensors_conf == next_sensors_conf):

                        fix_query = 'UPDATE ' + table + '_Activity_States SET activity = ? WHERE timestamp = ?'
                        row_fixed = cursor.execute(fix_query, [next_label, row[0]])
                        conn.commit()
                        fixed_elements.append(row)

                if(prev_label == None and next_label != None and curr_sensors_conf == next_sensors_conf):
                    fix_query = 'UPDATE ' + table + '_Activity_States SET activity = ? WHERE timestamp = ?'
                    row_fixed = cursor.execute(fix_query, [next_label, row[0]])
                    conn.commit()
                    fixed_elements.append(row)

            #Count the remaining row with 'label = None'
            query_rem2 = 'SELECT COUNT(*) FROM ' + table + '_Activity_States AS OA JOIN ' + sensors_tables[index] + '_Observation_Vectors AS OO\
            ON OA.timestamp = OO.timestamp WHERE OA.activity IS NULL'
            num_of_rem_rows = cursor.execute(query_rem2).fetchone()

            fix_again = False if (num_of_rem_rows == num_rows_not_fixed) else True
            print num_of_rem_rows
            rows_to_fix = remove_fixed_elements(fixed_elements, rows_to_fix)

        query_select = 'SELECT timestamp FROM ' + table +'_Activity_States WHERE activity IS NULL'
        timestamps_to_delete = cursor.execute(query_select).fetchall()

        for timestamp in timestamps_to_delete:
            print timestamp, table, sensors_tables[index]
            delete_adls_query = 'DELETE FROM ' + table + '_Activity_States WHERE timestamp = ?'
            cursor.execute(delete_adls_query, [timestamp[0]])
            conn.commit()
            delete_sensors_query = 'DELETE FROM ' + sensors_tables[index] + '_Observation_Vectors WHERE timestamp = ?'
            cursor.execute(delete_sensors_query, [timestamp[0]])
            conn.commit()

    print("\n### PRINTS FOR DEBUG PURPOSES MUST BE REMOVED ###")
    row = cursor.execute('SELECT COUNT(*) FROM OrdonezA_ADLs_Activity_States').fetchone()
    print row
    row = cursor.execute('SELECT COUNT(*) FROM OrdonezA_Sensors_Observation_Vectors').fetchone()
    print row
    row = cursor.execute('SELECT COUNT(*) FROM OrdonezB_ADLs_Activity_States').fetchone()
    print row
    row = cursor.execute('SELECT COUNT(*) FROM OrdonezB_Sensors_Observation_Vectors').fetchone()
    print row
    print("\n#################################################")
    conn.close()
    print '\nFixing procedure completed! :)'

def remove_fixed_elements(fixed_elements, rows_to_fix):
    for el in fixed_elements:
        rows_to_fix.remove(el)
    return rows_to_fix

def discretize_all():
    discretize_sensors()
    discretize_adls()
    remove_useless_data()
    fix_remaining_data()
