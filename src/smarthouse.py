#!/usr/bin/python
from utils import txt_to_csv
from preprocess import load_dataset, discretize_data

txt_to_csv.convert()
load_dataset.load()
discretize_data.discretize_all()
