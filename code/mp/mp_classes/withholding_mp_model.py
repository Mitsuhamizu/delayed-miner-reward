from math import exp

import numpy as np


def get_gamma_by_headstart(headstart):
    gamma = 0.5 + 4 * pow(10, -2) * headstart
    gamma = min(gamma, 1)
    gamma = max(gamma, 0)
    return gamma


class Withholding_mp:
    def __init__(self, adversary_setting, withholding_setting):
        self.adversary_setting = adversary_setting
        self.withholding_setting = withholding_setting

        self.compute_state_probability()
        self.compute_relative_revenue()
        self.adversary_extra_revenue = (
            self.adversary_relative_revenue - self.adversary_setting.get_alpha()
        )

    def compute_state_probability(self):
        pass

    def get_honest_block_share(self, p0, p0_prime, p1, alpha, gamma, exp_lambd):
        pass

    def get_adversary_block_share(self, p0, p0_prime, p1, alpha, gamma, exp_lambd):
        pass

    def compute_relative_revenue(self):
        pass

    def get_relative_revenue(self):
        return self.adversary_relative_revenue

    def get_extra_revenue(self):
        return self.adversary_extra_revenue

    def put_relative_revenue_into_dataframe(self, df):
        df[self.adversary_setting.get_alpha()][
            self.adversary_setting.get_gamma()
        ] = self.get_extra_revenue()
        return df


class Withholding_mp(Withholding_mp):
    def compute_state_probability(self):
        # load the related information.
        alpha = self.adversary_setting.get_alpha()
        lambd = self.withholding_setting.get_expectation()
        exp_lambd = np.exp(-lambd)
        denominator = (
            (1 - exp_lambd) * ((1 - alpha) + (1 - alpha) * alpha) + exp_lambd + alpha
        )
        p0 = ((1 - alpha) * (1 - exp_lambd) + exp_lambd) / denominator
        p0_prime = (alpha * (1 - alpha) * (1 - exp_lambd)) / denominator
        p1 = alpha / denominator

        # check the data is correct.
        np.testing.assert_almost_equal(p0 + p0_prime + p1, 1)
        np.testing.assert_almost_equal(p0, (1 - alpha) * p0 + p0_prime + exp_lambd * p1)
        np.testing.assert_almost_equal(p0_prime, (1 - exp_lambd) * (1 - alpha) * p1)
        np.testing.assert_almost_equal(p1, alpha * p0 + (1 - exp_lambd) * alpha * p1)

        self.p0 = p0
        self.p0_prime = p0_prime
        self.p1 = p1

    def compute_relative_revenue(self):
        # load the setting.
        p0, p0_prime, p1 = self.p0, self.p0_prime, self.p1
        alpha, gamma = (
            self.adversary_setting.get_alpha(),
            self.adversary_setting.get_gamma(),
        )
        lambd = self.withholding_setting.get_expectation()

        exp_lambd = np.exp(-lambd)
        # reward of honest miner.
        honest_blocks = self.get_honest_block_share(
            p0, p0_prime, p1, alpha, gamma, exp_lambd
        )
        # reward of adversary.
        adversary_blocks = self.get_adversary_block_share(
            p0, p0_prime, p1, alpha, gamma, exp_lambd
        )

        self.adversary_relative_revenue = adversary_blocks / (
            adversary_blocks + honest_blocks
        )

    def get_honest_block_share(self, p0, p0_prime, p1, alpha, gamma, exp_lambd):
        return (
            p0 * (1 - alpha) * 1
            + p0_prime * (1 - alpha) * (1 - gamma) * 2
            + p0_prime * (1 - alpha) * gamma * 1
        )

    def get_adversary_block_share(self, p0, p0_prime, p1, alpha, gamma, exp_lambd):
        return (
            p0_prime * alpha * 2
            + p0_prime * (1 - alpha) * gamma * 1
            + p1 * (1 - exp_lambd) * alpha * 1
            + p1 * exp_lambd * 1
        )
