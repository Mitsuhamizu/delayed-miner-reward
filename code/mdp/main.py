import csv
import os.path as op
import sys
from decimal import *

import mdptoolbox
import pandas as pd

sys.path.append(op.abspath(op.join(__file__, op.pardir, op.pardir)))

from mdp_helper.indexer import *
from mdp_helper.matrix import *
from mdp_helper.matrix_generation import *
from mdp_helper.probability_provider import *
from setting import *

if __name__ == "__main__":
    home_dir = op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir))
    path_to_data = home_dir + "/data/mdp/"

    result = pd.DataFrame(
        columns=alphas,
        index=gammas,
    )

    for lambd_iter in lambds:
        for gamma_iter in gammas:
            for alpha_iter in alphas:

                indexer = Indexer(rounds, fork_states_num, settlement_num)
                indexer.test()

                probability_provider = Probability_provider(
                    lambd_iter,
                    alpha_iter,
                    max_fork_len,
                )

                P, A, H = generate_matrixs(
                    indexer,
                    probability_provider,
                    alpha_iter,
                    gamma_iter,
                )

                low, high = 0, 1
                # UNDERPAYING
                while high - low > epsilon / 8:
                    rho = (low + high) / 2
                    R = [None] * action_num
                    # generate Reward with different rho.
                    for action in actions_lib:
                        R[action] = (1 - rho) * A[action] - rho * H[action]
                    rvi = mdptoolbox.mdp.RelativeValueIteration(
                        P, R, epsilon=epsilon / 8
                    )
                    rvi.run()

                    if rvi.average_reward > 0:
                        low = rho
                    else:
                        high = rho
                print(
                    "expectation: {}, alpha: {}, gamma: {}, rho: {:.4f}".format(
                        lambd_iter, alpha_iter, gamma_iter, rho
                    )
                )
        result.to_csv(
            path_to_data
            + "mdp/fork_length_{}/mdp_{:.2f}.csv".format(max_fork_len, lambd_iter),
            encoding="utf-8",
        )
