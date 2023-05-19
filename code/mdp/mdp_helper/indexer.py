from random import randrange

from global_variable import *
from setting import *


class Indexer:
    # init a list of indexer for fast locate the index of a state.
    def __init__(self, rounds, fork_states_num, settlement_num):

        self.rounds = rounds
        self.fork_states_num = fork_states_num
        self.settlement_num = settlement_num
        self.state_to_start_point = dict()
        self.index_to_state = (
            [1] * rounds * rounds * rounds * fork_states_num * settlement_num
        )

        current_index = 0

        for a in range(rounds):
            self.state_to_start_point[a] = dict()
            for h in range(rounds):
                self.state_to_start_point[a][h] = dict()
                a_prime_low_bound, a_prime_high_bound = self.get_alpha_prime_bound(a, h)

                for a_prime in range(a_prime_low_bound, a_prime_high_bound + 1):
                    self.state_to_start_point[a][h][a_prime] = current_index

                    for fork_state_iter in range(fork_states_num):
                        for settlement_iter in range(settlement_num):
                            self.index_to_state[
                                current_index
                                + settlement_iter * fork_states_num
                                + fork_state_iter
                            ] = (
                                a,
                                a_prime,
                                h,
                                fork_state_iter,
                                settlement_iter,
                            )
                    current_index += fork_states_num * settlement_num

        self.index_to_state = self.index_to_state[:current_index]

    def get_state_by_index(self, index):
        return self.index_to_state[index]

    def get_index_by_state(self, a, a_prime, h, f, s):
        return self.state_to_start_point[a][h][a_prime] + s * self.fork_states_num + f

    # Get a' range.
    def get_alpha_prime_bound(self, a, h):
        low_bound = self.get_low_bound_of_alpha_prime(a, h)
        high_bound = a
        return low_bound, high_bound

    def get_low_bound_of_alpha_prime(self, a, h):
        # If a >= h, it means adversary's chain is longer than the honest one.
        # At this point, the published adversary's chain must less or equal than
        # the honest one. Otherwise, there is no fork.
        if a - h < 0:
            return 0
        else:
            return a - h

    def verify_correctness_of_state(self, a, a_prime, h):
        low_bound = self.get_low_bound_of_alpha_prime(a, h)
        upper_bound = a
        if a_prime >= low_bound and a_prime <= upper_bound:
            return True
        else:
            return False

    # Only consider adversary's reward since honest miners never get reward after withholding (see the MDP table).
    def check_settlement_after_withholding(self, reward):
        if reward > 0:
            return SETTLED
        elif reward == 0:
            return UNSETTLED

    # input:
    # 1. state: the state before the action and timeout.
    # 2. mined_block: the block number from two parties within the withholding.
    # 3. action_type: the action the adversary adopts.
    # 4. label: label for cases under "WAIT_WITH_MATCH" and "WAIT_IN_ACITVE",
    # which is used for subdividing the cases.

    # For actions in ["OVERRIDE", "WAIT_WITH_OVERRIDE", "WAIT_WITHOUT_OVERRIDE"]
    # the label should be none since we do not need more info to get the states.

    # For "WAIT_WITH_MATCH" and "WAIT_IN_ACTIVE", there are 2 label
    # 1. corrupt_block
    # 2. honest_block
    # The label denote the identity of the producer of first honest block after match.

    def get_index_after_timeout(
        self,
        state,
        mined_block,
        action_type,
        reward_type,
        adversary_reward,
    ):
        # unpack data.
        (a_mined, h_mined) = mined_block
        a, a_prime, h = state

        # Most fork state after withholding is inactive, so we just set the default value as inactive.
        fork_after_withholding = INACTIVE

        no_block_label, corrupt_label, honest_label = (
            "no_honest_block_after_match",
            "corrupt_block",
            "honest_block",
        )

        if action_type == "OVERRIDE":

            if h_mined == 0:
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a - h - 2 + a_mined,
                    a - h - 2 + a_mined,
                    0,
                )
            else:
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a - h - 1 + a_mined,
                    a - h - 2 + a_mined,
                    h_mined,
                )

        elif action_type == "WAIT_WITHOUT_OVERRIDE":
            if h_mined == 0:
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a + a_mined,
                    a_prime - 1 + a_mined,
                    h,
                )
            else:
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a + a_mined,
                    a_prime - 1 + a_mined,
                    h + h_mined,
                )

        elif action_type == "WAIT_WITH_OVERRIDE":
            if h_mined == 0:
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a - h - 1 + a_mined,
                    a - h - 1 + a_mined,
                    0,
                )
            else:
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a + a_mined,
                    a_prime + a_mined - 1,
                    h + h_mined,
                )

        elif action_type == "WAIT_WITH_MATCH":
            if reward_type == no_block_label:
                (
                    a_after_withholding,
                    a_prime_after_withholding,
                    h_after_withholding,
                    fork_after_withholding,
                ) = (a + a_mined, a_mined, h + h_mined, ACTIVE)
            elif reward_type == corrupt_label:
                (
                    a_after_withholding,
                    a_prime_after_withholding,
                    h_after_withholding,
                ) = (a_mined, a_mined, h + h_mined - a)
            elif reward_type == honest_label:
                (
                    a_after_withholding,
                    a_prime_after_withholding,
                    h_after_withholding,
                ) = (a + a_mined, a_mined, h + h_mined)

        elif action_type == "WAIT_IN_ACTIVE":
            if reward_type == no_block_label:
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a - h - 1 + a_mined,
                    a - h - 1 + a_mined,
                    0,
                )
            elif reward_type == corrupt_label:
                (
                    a_after_withholding,
                    a_prime_after_withholding,
                    h_after_withholding,
                ) = (
                    a - h + a_mined,
                    a - h - 1 + a_mined,
                    h_mined,
                )
            elif reward_type == honest_label:
                (
                    a_after_withholding,
                    a_prime_after_withholding,
                    h_after_withholding,
                ) = (
                    a + a_mined,
                    a - h - 1 + a_mined,
                    h + h_mined,
                )
        elif action_type == "WAIT_IN_ACTIVE_WITH_MATCH":
            if reward_type == "corrupt_and_no":
                (
                    a_after_withholding,
                    a_prime_after_withholding,
                    h_after_withholding,
                    fork_after_withholding,
                ) = (a_prime + a_mined, a_mined, a_prime, ACTIVE)
            elif reward_type == "*_and_corrupt":
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a_mined,
                    a_mined,
                    h_mined - a_prime,
                )
            elif reward_type == "corrupt_and_honest":
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a_prime + a_mined,
                    a_mined,
                    h_mined,
                )
            elif reward_type == "honest_and_no":
                (
                    a_after_withholding,
                    a_prime_after_withholding,
                    h_after_withholding,
                    fork_after_withholding,
                ) = (a + a_mined, a_mined, h + h_mined, ACTIVE)
            elif reward_type == "honest_and_honest":
                a_after_withholding, a_prime_after_withholding, h_after_withholding = (
                    a + a_mined,
                    a_mined,
                    h + h_mined,
                )
        settlement_after_withholding = self.check_settlement_after_withholding(
            adversary_reward
        )
        index = self.get_index_by_state(
            a_after_withholding,
            a_prime_after_withholding,
            h_after_withholding,
            fork_after_withholding,
            settlement_after_withholding,
        )
        return index

    def test(self):
        for _ in range(10000):
            rounds = self.rounds
            a_expect = randrange(rounds)
            h_expect = randrange(rounds)
            a_prime_expect = randrange(rounds)
            f_expect = randrange(self.fork_states_num)
            s_expect = randrange(self.settlement_num)

            is_legal = self.verify_correctness_of_state(
                a_expect, a_prime_expect, h_expect
            )

            if is_legal:
                index = self.get_index_by_state(
                    a_expect, a_prime_expect, h_expect, f_expect, s_expect
                )
                (
                    a_actual,
                    a_prime_actual,
                    h_actual,
                    f_actual,
                    s_actual,
                ) = self.get_state_by_index(index)

                error_text = "\nexpect: a: {}, a': {}, h: {}, f: {}, s:{}\nactual: a: {}, a': {}, h: {}, f: {}, s:{}".format(
                    a_expect,
                    a_prime_expect,
                    h_expect,
                    f_expect,
                    s_expect,
                    a_actual,
                    a_prime_actual,
                    h_actual,
                    f_actual,
                    s_actual,
                )

                assert a_expect == a_actual, error_text
                assert a_prime_expect == a_prime_actual, error_text
                assert h_expect == h_actual, error_text
                assert f_expect == f_actual, error_text
                assert s_expect == s_actual, error_text
            else:
                assert a_prime_expect > a_expect or a_prime_expect < a_expect - h_expect
