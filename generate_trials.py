import numpy as np
import os
import datetime

a = np.array([1, 2, 3, 4])

trial_data = np.append(a, [1,.789])
trial_data = np.insert(trial_data, 0, [5,99])
trial_data = [trial_data, "blah"]


print(trial_data)
