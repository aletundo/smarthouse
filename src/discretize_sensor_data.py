import pandas as pd
import sqlite3, os, glob, datetime
from os.path import basename

# Change directory to the script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

db_dir = '../db/'

conn = sqlite3.connect(db_dir + 'example.db')
cursor =  conn.cursor()

def next_time_slice(tm, secs):
    fulldate = datetime.datetime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate

timeslice = datetime.datetime(2011, 11, 28, 02, 27, 59)
while (timeslice < datetime.datetime(2011, 12, 12, 07, 22, 21)):
    next_slice = next_time_slice(timeslice, 60)
    rows = cursor.execute('SELECT * FROM OrdonezA_Sensors WHERE datetime(start_time) >= ? AND datetime(start_time) <= ?', [timeslice, next_slice])
    for row in rows:
        print row[3]
    timeslice = next_slice
conn.close()
