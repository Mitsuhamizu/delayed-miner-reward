import numpy as np
from utils.misc.assert_utils import *
from utils.misc.logger import *


class Probability_provider:
    # init a list of indexer for fast locate the index of a state.
    def __init__(self, expectation, alpha, max_fork_len):
        self.max_fork_len = max_fork_len
        # 1. generate default probabilities.
        (
            self.adversary_probabilities,
            self.honest_probabilities,
        ) = self.generate_truncated_probabilities_for_both_parties(
            expectation, alpha, max_fork_len
        )

        self.probabilities = self.generate_combineds_probabilities()
        self.adversary_hashrate = alpha

    def get_probabilities(self, a, h):

        return self.probabilities[a][h]

    def get_poisson_probability(self, k, lambd):
        return lambd ** k * np.exp(-lambd) / np.math.factorial(k)

    # output: truncated probabilities list for adversary and honest miner.
    def generate_truncated_probabilities_for_both_parties(
        self, expectation, alpha, block_upper_bound, epsilon=10e-10
    ):

        # init two empty list and lambd.
        adversary_list, honest_list = np.zeros([block_upper_bound + 1]), np.zeros(
            [block_upper_bound + 1]
        )

        adversary_list = self.get_truncated_probabilities(
            alpha, expectation, block_upper_bound, epsilon
        )
        honest_list = self.get_truncated_probabilities(
            1 - alpha, expectation, block_upper_bound, epsilon
        )

        return adversary_list, honest_list

    def generate_combineds_probabilities(self):
        probabilities = {}
        max_fork_len = self.max_fork_len

        # 1. get the upper bound.
        block_upper_bound_a_default = len(self.adversary_probabilities) - 1
        block_upper_bound_h_default = len(self.honest_probabilities) - 1

        for a in range(max_fork_len):
            probabilities[a] = {}
            for h in range(max_fork_len):

                # 2. generate truncated according to specific a and h.
                # If the bound of fork length is reached firstly, just advance the cutoff value.
                block_upper_bound_a = min(max_fork_len - a, block_upper_bound_a_default)
                block_upper_bound_h = min(max_fork_len - h, block_upper_bound_h_default)

                current_adversary_probabilities = self.cut_probabilities_off(
                    self.adversary_probabilities, block_upper_bound_a
                )
                current_honest_probabilities = self.cut_probabilities_off(
                    self.honest_probabilities, block_upper_bound_h
                )

                # 3. combine the probabilities of adversary and honest.
                probabilities[a][h] = self.generate_combined_probabilities(
                    current_adversary_probabilities,
                    current_honest_probabilities,
                )

        return probabilities

    # cut off according to different inital height.
    def cut_probabilities_off(self, probabilities, cutoff):
        probabilities = probabilities[:cutoff]

        probabilities = np.append(
            probabilities,
            np.float(1) - np.sum(probabilities),
        )

        assert_all_non_negative_and_equal_one(probabilities)
        return probabilities

    # combine the result of hoenst mining blocks and adversary mining blocks.
    def generate_combined_probabilities(
        self,
        truncated_adversary_probabilities,
        truncated_honest_probabilities,
    ):

        result = np.zeros(
            (
                len(truncated_adversary_probabilities),
                len(truncated_honest_probabilities),
            )
        )

        for a_idx, a_val in enumerate(truncated_adversary_probabilities):
            for h_idx, h_val in enumerate(truncated_honest_probabilities):
                result[a_idx][h_idx] += a_val * h_val
        np.testing.assert_almost_equal(sum(sum(result)), 1)
        return result

    # output: truncated probabilities list.
    def get_truncated_probabilities(self, alpha, lambd, block_upper_bound, epsilon):
        probability_list = np.zeros([block_upper_bound + 1])
        try:
            for block in range(block_upper_bound):
                current_probability = self.get_poisson_probability(block, alpha * lambd)
                if current_probability < epsilon:
                    raise StopIteration
                probability_list[block] = current_probability
        except StopIteration:
            probability_list = probability_list[:block]
        else:
            probability_list = probability_list[: block + 1]

        probability_list[-1] += np.float(1) - np.sum(probability_list)

        assert_all_non_negative_and_equal_one(probability_list)

        return probability_list

    def get_block_diff_probabilities(self):
        (
            probabilities,
            a_block_bound,
            h_block_bound,
        ) = self.get_probabilities_and_block_num_bound(0, 0)
        keys = [-i for i in reversed(range(1, h_block_bound + 1))] + [
            i for i in range(a_block_bound + 1)
        ]

        diff_probabilities = dict()
        for key in keys:
            diff_probabilities[key] = 0

        diff_probabilities[0] += probabilities["none"][0]

        for adversary_blocks in range(1, a_block_bound + 1):
            diff_probabilities[adversary_blocks] += probabilities["ad"][
                adversary_blocks - 1
            ]
        for honest_blocks in range(1, h_block_bound + 1):
            diff_probabilities[-honest_blocks] += probabilities["h"][honest_blocks - 1]

        for adversary_blocks in range(1, a_block_bound + 1):
            for honest_blocks in range(1, h_block_bound + 1):
                diff_probabilities[adversary_blocks - honest_blocks] += probabilities[
                    "both"
                ][(adversary_blocks - 1) * (h_block_bound) + (honest_blocks - 1)]

        return diff_probabilities
