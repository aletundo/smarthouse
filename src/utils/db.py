import sqlite3, os

def get_conn():
    db_dir = '../../db/'
    # Make db sub directory if not exists
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(db_dir + 'smarthouse.db')
    conn.row_factory = sqlite3.Row
    return conn
