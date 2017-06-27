import sqlite3, os

def get_conn():
    # Change directory to the script directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    db_dir = '../../../db/'
    # Make db sub directory if not exists
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(db_dir + 'smarthouse.db')
    return conn
