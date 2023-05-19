import numpy as np
from scipy.sparse import coo_matrix as sparse_coo


class Matrix:
    # init a list of indexer for fast locate the index of a state.
    def __init__(self, length):
        self.row = np.zeros([length])
        self.col = np.zeros([length])
        self.p = np.zeros([length])
        self.a = np.zeros([length])
        self.h = np.zeros([length])
        self.cursor = 0

    def add_element(self, row, col, p, a):
        assert p >= 0, p
        assert a >= 0, a
        self.row[self.cursor] = row
        self.col[self.cursor] = col
        self.p[self.cursor] = p
        self.a[self.cursor] = a
        self.cursor += 1

    def transfer_to_sparse(self, states_num):
        self.cut_elements_off()

        P = sparse_coo(
            (self.p, (self.row, self.col)),
            shape=[states_num, states_num],
        ).tocsr()

        A = sparse_coo(
            (self.a, (self.row, self.col)), shape=[states_num, states_num], dtype=int
        ).tocsr()

        H = sparse_coo(
            (self.h, (self.row, self.col)), shape=[states_num, states_num], dtype=int
        ).tocsr()
        return P, A, H

    def cut_elements_off(self):
        self.row = self.row[: self.cursor]
        self.col = self.col[: self.cursor]
        self.p = self.p[: self.cursor]
        self.a = self.a[: self.cursor]
        self.h = self.h[: self.cursor]

    def add_elements_when_withholding(
        self, index, action_raw, indexer, probability_provider, gamma=None
    ):

        a, a_prime, h, f, s = indexer.get_state_by_index(index)
        state_before_action = (a, a_prime, h)

        # x_after_action is the states after action but not transited states.
        # There are five type of actions involving withholding.
        # OVERRIDE, WAIT_WITH_OVERRRIDE, WAIT_WITHOUT_OVERRIDE, WAIT_IN_ACTIVE, WAIT_WITH_MATCH.

        if action_raw == "OVERRIDE":
            a_after_action, a_prime_after_action, h_after_action = (
                a - h - 1,
                a - h - 1,
                0,
            )
            reward = {"no_honest_block": h + 2, "has_honest_block": h + 1}
        elif action_raw == "WAIT_WITHOUT_OVERRIDE":
            a_after_action, a_prime_after_action, h_after_action = (
                a,
                a_prime,
                h,
            )
            reward = {"no_honest_block": 0, "has_honest_block": 0}

        elif action_raw == "WAIT_WITH_OVERRIDE":
            a_after_action, a_prime_after_action, h_after_action = (
                a,
                a_prime,
                h,
            )
            reward = {"no_honest_block": h + 1, "has_honest_block": 0}

        elif action_raw == "WAIT_IN_ACTIVE":
            a_after_action, a_prime_after_action, h_after_action = (
                a,
                a_prime,
                h,
            )
            reward = {
                "no_honest_block_after_match": h + 1,
                "corrupt_block": h,
                "honest_block": 0,
            }

        probabilities = probability_provider.get_probabilities(
            a_after_action, h_after_action
        )

        for a_mined, h_mined in np.ndindex(probabilities.shape):
            mined_block_num = (a_mined, h_mined)

            # code for allowing match when wait in active:
            # if h < a and a <= h + h_mined and "WAIT" in action_raw:

            # WAIT_WITH_MATCH has highest priority in WAIT.
            # We postponed it to now since we need to know # of honest block in withholding.
            with_match_candidates = [
                "WAIT_WITH_OVERRIDE",
                "WAIT_WITHOUT_OVERRIDE",
                "WAIT_IN_ACTIVE",
            ]

            if h < a and a <= h + h_mined and action_raw in with_match_candidates:
                if action_raw == "WAIT_IN_ACTIVE":
                    action_executed = "WAIT_IN_ACTIVE_WITH_MATCH"

                    reward_executed = {
                        "corrupt_and_no": h,
                        "corrupt_and_honest": h,
                        "honest_and_no": 0,
                        "honest_and_honest": 0,
                        "*_and_corrupt": a,
                    }

                else:
                    action_executed = "WAIT_WITH_MATCH"
                    reward_executed = {
                        "no_honest_block_after_match": 0,
                        "corrupt_block": a,
                        "honest_block": 0,
                    }
            else:
                action_executed = action_raw
                reward_executed = reward

            if h_mined == 0:
                reward_type = "no_honest_block"
            elif h_mined > 0:
                reward_type = "has_honest_block"

            # mean "has_honest_block" in "WAIT_WITH_MATCH" or "WAIT_IN_ACTIVE"
            # we need to subdivide "has_honest_block"
            if action_executed in [
                "WAIT_WITH_MATCH",
                "WAIT_IN_ACTIVE",
                "WAIT_IN_ACTIVE_WITH_MATCH",
            ]:

                # decide the parameter combinations.
                if action_executed == "WAIT_WITH_MATCH":
                    # If there is no new block after the match.
                    if a == h + h_mined:
                        parameter_combination = [(1, "no_honest_block_after_match")]
                    # If there are new blocks after the match,
                    # the next state is decided by gamma.
                    elif a < h + h_mined:
                        parameter_combination = [
                            (gamma, "corrupt_block"),
                            (1 - gamma, "honest_block"),
                        ]
                elif action_executed == "WAIT_IN_ACTIVE_WITH_MATCH":
                    if a == h + h_mined:
                        parameter_combination = [
                            (gamma, "corrupt_and_no"),
                            (1 - gamma, "honest_and_no"),
                        ]
                    # If there are new blocks after the match,
                    # the next state is decided by gamma.
                    elif a < h + h_mined:
                        parameter_combination = [
                            (gamma, "*_and_corrupt"),
                            (gamma * (1 - gamma), "corrupt_and_honest"),
                            ((1 - gamma) * (1 - gamma), "honest_and_honest"),
                        ]
                elif action_executed == "WAIT_IN_ACTIVE":
                    # Same as above.
                    if h_mined == 0:
                        parameter_combination = [(1, "no_honest_block_after_match")]
                    elif h_mined > 0:
                        parameter_combination = [
                            (gamma, "corrupt_block"),
                            (1 - gamma, "honest_block"),
                        ]

                for (factor, reward_type) in parameter_combination:

                    self.add_element(
                        index,
                        indexer.get_index_after_timeout(
                            state_before_action,
                            mined_block_num,
                            action_executed,
                            reward_type,
                            reward_executed[reward_type],
                        ),
                        probabilities[a_mined][h_mined] * factor,
                        reward_executed[reward_type],
                    )
            else:

                self.add_element(
                    index,
                    indexer.get_index_after_timeout(
                        state_before_action,
                        mined_block_num,
                        action_executed,
                        None,
                        reward_executed[reward_type],
                    ),
                    probabilities[a_mined][h_mined],
                    reward_executed[reward_type],
                )
