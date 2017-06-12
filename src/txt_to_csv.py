#!/usr/bin/python
import pandas as pd
import os
import glob
from os.path import basename
import argparse

def set_directories(source, dest):
    """Set the dataset source and destion directories

    Args:
        source (str): The dataset source directory path.
        dest (str): The dataset destination directory path.

    Returns:
        dataset_dir (str): The dateset directory.
        csv_dir (str): The csv destination directory.
    """
    # Change directory to the script directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    dataset_dir = source
    if dest == 'csv/':
        csv_dir = source + dest
    else:
        csv_dir = dest

    # Make csv sub directory if not exists
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    return dataset_dir, csv_dir

def fix_headers(csv_dir):
    """Fix the csv files headers

    Args:
        csv_dir (str): The dataset csv files directory.

    """
    # Lowercase headers and replace their whitespaces with underscores
    for file in glob.glob(csv_dir + '*.csv'):
        with open(file, 'r') as fr:
            data = fr.readlines()
            header_line = data.pop(0)
            header_line = header_line.replace(' ', '_').lower()
        fr.close()
        with open(file, 'w') as fw:
            fw.writelines(header_line)
            fw.writelines(data)
        fw.close()

def convert(source='../dataset/', dest='csv/', skip_rows = [1,1], source_separator='\ *\t+\ *\t*|\ *\ +\ *\ +', dest_separator = ','):
    """Convert the txt dataset into csv

    Args:
        source (str): The dataset source directory path.
        dest (str): The dataset destination directory path.
        skip_rows (list): The txt files rows to skip.
        source_separator (str): The separator of the txt columns.
        dest_separator (str): The separator of the csv columns.

    """
    #Set the directories
    dataset_dir, csv_dir = set_directories(source, dest)

    # Read txt files and convert them into csv
    for file in glob.glob(dataset_dir + '*.txt'):
        data_frame = pd.read_csv(file, engine = 'python', skiprows = skip_rows, sep = source_separator, header = 0, skipinitialspace = True)
        # Strip headers
        data_frame.columns = data_frame.columns.str.strip()
        csv_name = os.path.splitext(basename(file))[0]
        data_frame.to_csv(csv_dir + csv_name + '.csv', sep = dest_separator, index =  False, encoding = 'utf-8')

    #Fix the csv files headers
    fix_headers(csv_dir)

    print ("\n\nConversion completed! :)\nCsv files are in %s\n\n" % os.path.realpath(csv_dir))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is an utility script to convert txt files into csv.\n\
    It requires a source and a destination directory.\
    If destination is not specified it creates a \'csv\' directory in source directory.\n\
    Read further for more information.')

    parser.add_argument('-s','--source', help='Source directory absolute path', default='../dataset/')
    parser.add_argument('-d','--dest', help='Destination directory absolute path', default='csv/')
    parser.add_argument('-ssep','--sourceseparator', help='Txt separator. It accepts regex too (use \'\').', default='\ *\t+\ *\t*|\ *\ +\ *\ +')
    parser.add_argument('-dsep','--destseparator', help='Csv separator. It accepts regex too (use \'\').', default=',')
    parser.add_argument('-skip','--skiprows', help='Txt files rows to skip. It accepts a list [] to specificy a range.', nargs='*', default=[1,1])
    args = parser.parse_args()

    convert(args.source, args.dest, args.skiprows, args.sourceseparator, args.destseparator)
