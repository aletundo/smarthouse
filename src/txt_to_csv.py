import pandas as pd
import os
import glob
from os.path import basename

# Change directory to the script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

dataset_dir = '../UCI_ADL_Binary_Dataset/'
csv_dir = dataset_dir + 'csv/'

# Make csv sub directory if not exists
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

for file in glob.glob(dataset_dir + '*.txt'):
    data_frame = pd.read_csv(file, engine = 'python', skiprows = [1, 1], sep = '\t+\ *\t*', header = 0, skipinitialspace = True)
    # Strip whitespace from headers
    data_frame.columns = data_frame.columns.str.strip()
    csv_name = os.path.splitext(basename(file))[0]
    data_frame.to_csv(csv_dir + csv_name + '.csv', sep = ',', index =  False, encoding = 'utf-8')
