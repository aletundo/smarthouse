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

fm_mean_a, fm_mean_b, fm_std_a, fm_std_b, precision_mean_a, precision_mean_b, recall_mean_a, recall_mean_b, accuracy_final_list_a, accuracy_final_list_b, conf_matrix_a, conf_matrix_b = hmm_performance.final_test()

print ("\nLabels accuracy mean OrdonezA:\n%s\n" % accuracy_final_list_a)
print ("\nLabels accuracy mean OrdonezB:\n%s\n" % accuracy_final_list_b)

print ("\nConfusion matrix OrdonezA:\n%s\n" % conf_matrix_a)
print ("\nConfusion matrix OrdonezB:\n%s\n" % conf_matrix_b)

print ("\nPrecision mean OrdonezA:\n%s\n" % precision_mean_a)
print ("\nPrecision mean OrdonezB:\n%s\n" % precision_mean_b)

print ("\nRecall mean OrdonezA:\n%s\n" % recall_mean_a)
print ("\nRecall mean OrdonezB:\n%s\n" % recall_mean_b)

print ("\nFMeasure mean dataset OrdonezA:\n%s\n" % fm_mean_a)
print ("\nFMeasure std dataset OrdonezA:\n%s\n" % fm_std_a)

print ("\nFMeasure mean dataset OrdonezB:\n%s\n" % fm_mean_b)
print ("\nFMeasure std dataset OrdonezB:\n%s\n" % fm_std_b)
