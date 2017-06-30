#!/usr/bin/python
import os, numpy as np, operator
from computing.utils import txt_to_csv, db
from computing.preprocess import load_dataset, discretize_data
from computing.hmm import hmm_init, hmm_performance
from datetime import datetime, timedelta
from hidden_markov import hmm

# Change directory to the script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# txt_to_csv.convert()
# load_dataset.load()
# discretize_data.discretize_all()

fm_a, fm_b, fm_std_a, fm_std_b, labels_acc_a, labels_acc_b = hmm_performance.final_test()

print ("\nLabels accuracy mean OrdonezA:\n%s\n" % labels_acc_a)
print ("\nLabels accuracy mean OrdonezB:\n%s\n" % labels_acc_b)

print ("\nFMeasure mean dataset OrdonezA:\n%s\n" % fm_a)
print ("\nFMeasure std dataset OrdonezA:\n%s\n" % fm_std_a)
print ("\nFMeasure mean dataset OrdonezB:\n%s\n" % fm_b)
print ("\nFMeasure std dataset OrdonezB:\n%s\n" % fm_std_b)
