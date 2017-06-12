import pandas as pd
import sqlite3, os, glob, time, re
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
conn.close()
