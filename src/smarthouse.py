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
random_results, dataset_results, manual_results = hmm_performance.obs_probability_test('OrdonezA', datetime(2011, 11, 28, 0, 0, 0), datetime(2011, 12, 11, 0, 0, 0))
random_results, dataset_results, manual_results = hmm_performance.obs_probability_test('OrdonezB', datetime(2012, 11, 12, 0, 0, 0), datetime(2012, 12, 02, 0, 0, 0))

print("\n############### Ordonez A ###############")
print ("\nConfusion matrix:\n%s\n" % conf_matrix_a)
print ("\nLabels accuracy mean:\n%s\n" % accuracy_final_list_a)
print ("\nPrecision mean:\n%s\n" % precision_mean_a)
print ("\nRecall mean:\n%s\n" % recall_mean_a)
print ("\nFMeasure mean dataset:\n%s\n" % fm_mean_a)
print ("\nFMeasure std dataset:\n%s\n" % fm_std_a)
print ("\nRandom observations probabilities:\n%s\n" % random_results)
print ("\nDataset observations probabilities:\n%s\n" % dataset_results)
print ("\nManual observations probabilities:\n%s\n" % manual_results)
print("\n#########################################")

print("\n############### Ordonez B ###############")
print ("\nConfusion matrix:\n%s\n" % conf_matrix_b)
print ("\nLabels accuracy mean:\n%s\n" % accuracy_final_list_b)
print ("\nPrecision mean:\n%s\n" % precision_mean_b)
print ("\nRecall mean:\n%s\n" % recall_mean_b)
print ("\nFMeasure mean dataset:\n%s\n" % fm_mean_b)
print ("\nFMeasure std dataset:\n%s\n" % fm_std_b)
print ("\nRandom observations probabilities:\n%s" % random_results)
print ("\nDataset observations probabilities:\n%s" % dataset_results)
print ("\nManual observations probabilities:\n%s" % manual_results)
print("\n#########################################")
