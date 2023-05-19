from math import exp
from ssl import DefaultVerifyPaths

FIRST_STAGE = 1
SECOND_STAGE = 2


def get_probability(lambd):
    return exp(-lambd)


def get_hashrate_without_block(x, stage_type):
    if stage_type == FIRST_STAGE:
        return 1 - 11 / 300 * pow(x, 2)
    elif stage_type == SECOND_STAGE:
        return float(0.9175 + 0.9175 * (exp(-44 / 367 * (x - 1.5)) - 1))


class Headstart_calculator:
    def __init__(self, step):
        self.step = step
        self.lambd = 1 / 600
        self.max_propagation_time = 60
        self.bins = int(self.max_propagation_time / step)

        hashrate_ratio_per_second = []

        for x_iter in range(0, self.bins + 1, 1):
            x_iter *= step
            if x_iter < 1.5:
                stage_type = FIRST_STAGE
            else:
                stage_type = SECOND_STAGE
            hashrate_iter = get_hashrate_without_block(x_iter, stage_type)
            hashrate_ratio_per_second.append(hashrate_iter)

        self.hashrate_ratio_per_second = hashrate_ratio_per_second

    def get_prob_without_fork_per_sec(self, hashrate_ratio_per_second, hashrate):
        lambd, step = self.lambd, self.step
        prob_without_fork_per_sec = []
        for idx, ratio in enumerate(hashrate_ratio_per_second[:-1]):
            next_ratio = hashrate_ratio_per_second[idx + 1]
            hashrate_without_block = (1 - hashrate) * (ratio + next_ratio) / 2

            prob_without_fork_iter = get_probability(
                lambd * hashrate_without_block * step
            )
            prob_without_fork_per_sec.append(prob_without_fork_iter)

        return prob_without_fork_per_sec

    def pad_hashrate_ratio(self, hashrate_ratio_per_second, delay):
        padding_bins = int(delay / self.step)
        padding_prefix = [1] * padding_bins
        hashrate_ratio_per_second = padding_prefix + hashrate_ratio_per_second

        return hashrate_ratio_per_second

    def get_prob_first_fork(self, prob_without_fork_per_sec):
        prob_without_fork_so_far = [1]
        prob_first_fork_in_sec = []
        for idx, prob in enumerate(prob_without_fork_per_sec):
            prob_without_fork_so_far.append(prob_without_fork_so_far[idx - 1] * prob)
            prob_first_fork_in_sec.append(prob_without_fork_so_far[idx] * (1 - prob))
        return prob_first_fork_in_sec

    def normalize_prob(self, prob_first_fork_in_sec):
        total_probability = sum(prob_first_fork_in_sec)
        prob_first_fork_in_sec = [i / total_probability for i in prob_first_fork_in_sec]

        return prob_first_fork_in_sec

    def get_headstart(self, hashrate, delay):
        step = self.step
        headstart = 0

        hashrate_ratio_per_second = self.hashrate_ratio_per_second
        hashrate_ratio_per_second = self.pad_hashrate_ratio(
            hashrate_ratio_per_second, delay
        )

        prob_without_fork_per_sec = self.get_prob_without_fork_per_sec(
            hashrate_ratio_per_second, hashrate
        )
        prob_first_fork_in_sec = self.get_prob_first_fork(prob_without_fork_per_sec)
        prob_first_fork_in_sec = self.normalize_prob(prob_first_fork_in_sec)

        released_time = 0
        for idx, prob in enumerate(prob_first_fork_in_sec):
            time = idx * step + step / 2
            released_time += time * prob
        released_time = released_time * 12.5 / self.max_propagation_time
        # released_time = released_time
        headstart = released_time - delay
        return headstart
