import os.path as op
import sys

sys.path.append(op.abspath(op.join(__file__, op.pardir, op.pardir)))
from global_variable.symbols import *
from utils.misc.logger import *

epsilon = 0.0001

actions_text = {ADOPT: "ADOPT", OVERRIDE: "OVERRIDE", WAIT: "WAIT"}

# For real world.
max_fork_len = 60
gammas = [0, 0.5, 1]
alphas = [round((i * 0.05), 2) for i in range(11)]
lambds = [1 / 30, 1 / 12, 1 / 2, 1, 2, 5, 10]

rounds = max_fork_len + 1
action_num, fork_states_num, settlement_num = (
    len(actions),
    len(states),
    len(settlement_values),
)
