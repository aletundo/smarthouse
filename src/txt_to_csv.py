import pandas as pd
import os

dataset_dir = '../UCI_ADL_Binary_Dataset/'
csv_dir = dataset_dir + 'csv/'

# Make csv sub directory
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

# Read A user .txt dataset files
A_ADLs = pd.read_csv(dataset_dir + 'OrdonezA_ADLs.txt', engine = 'python', skiprows = [0, 1], sep = '\t+\ *\t*', header = None, skipinitialspace = True)
A_Sensors = pd.read_csv(dataset_dir + 'OrdonezA_Sensors.txt', engine = 'python', skiprows = [0, 1], sep = '\t+\ *\t*', header = None, skipinitialspace = True)

# Read B user .txt dataset files
B_ADLs = pd.read_csv( dataset_dir + 'OrdonezB_ADLs.txt', engine = 'python',skiprows = [0, 1], sep = '\t+\ *\t*', header = None, skipinitialspace = True)
B_Sensors = pd.read_csv(dataset_dir + 'OrdonezB_Sensors.txt', engine = 'python', skiprows = [0, 1], sep = '\t+\ *\t*', header = None, skipinitialspace = True)

# Write A user .csv dataset files into csv sub directory
A_ADLs.to_csv(csv_dir + 'OrdonezA_ADLs.csv', sep = ',', index =  False, encoding = 'utf-8', header = ['start_time', 'end_time', 'activity'])
A_Sensors.to_csv(csv_dir + 'OrdonezA_Sensors.csv', sep = ',', index =  False, encoding = 'utf-8', header = ['start_time', 'end_time', 'location', 'type', 'place'])

# Write B user .csv dataset files into csv sub directory
B_ADLs.to_csv(csv_dir + 'OrdonezB_ADLs.csv', sep = ',', index =  False, encoding = 'utf-8', index_label = ['start_time', 'end_time', 'activity'])
B_Sensors.to_csv(csv_dir + 'OrdonezB_Sensors.csv', sep = ',', index =  False, encoding = 'utf-8', header = ['start_time', 'end_time', 'location', 'type', 'place'])
