import os.path as op
import sys

sys.path.append(op.abspath(op.join(__file__, op.pardir)))
from mp_classes.withholding_setting import *

gammas = [0, 0.5, 1]
block_interval = 600
withholding_time_bounds = [3, 6, 12, 30]
alphas = [i / 10 for i in range(0, 11)]
adversary_settings, withholding_settings = [], []

# init the settings.
for withholding_time_bound_iter in withholding_time_bounds:
    withholding_settings.append(
        Withholding_setting(withholding_time_bound_iter, block_interval)
    )
