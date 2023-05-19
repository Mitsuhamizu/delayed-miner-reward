import os
import os.path as op
import sys

sys.path.append(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)))
from utils.misc.logger import *

logger_home_dir = op.abspath(op.join(__file__, op.pardir, op.pardir))
mdp_logger_file = logger_home_dir + "/log/mdp_solver/solver.log"

# remove the logger file.
if op.isfile(mdp_logger_file):
    os.remove(mdp_logger_file)

# mdp_solver = my_custom_logger(mdp_logger_file, level=logging.DEBUG)
mdp_solver = my_custom_logger(mdp_logger_file, level=logging.INFO)
