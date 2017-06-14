#!/usr/bin/python
import os
from utils import txt_to_csv
from preprocess import load_dataset, discretize_data
from hmm import hmm_init
from datetime import datetime

# Change directory to the script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

txt_to_csv.convert()
load_dataset.load()
discretize_data.discretize_all()
