import numpy as np
import os

blocks = 2

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

# read in input files
design_filename = os.path.join(script_dir, "input_files/UNW01_stg1_certain.csv")
stg1_design = np.genfromtxt(design_filename, delimiter=',', skip_header = True, dtype = int)

stg1_trials = np.empty((0,3), int)

for b in range(0,blocks):

    newPerm = np.random.permutation(len(stg1_design)) # shuffles rows
    stg1_trials = np.append(stg1_trials, stg1_design[newPerm], axis = 0)

print(stg1_trials)