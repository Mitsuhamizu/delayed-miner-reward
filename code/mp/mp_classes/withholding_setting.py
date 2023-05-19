class Withholding_setting:
    def __init__(self, withholding_time_bound, block_interval):
        self.withholding_time_bound = withholding_time_bound
        self.block_interval = block_interval
        self.expectation = self.compute_expectation()

    def compute_expectation(self):
        return self.withholding_time_bound / self.block_interval

    def get_block_interval(self):
        return self.block_interval

    def get_withholding_time_bound(self):
        return self.withholding_time_bound

    def get_expectation(self):
        return self.expectation


class Withholding_setting_new:
    def __init__(self, withholding_time_bound, block_interval):
        self.withholding_time_bound = withholding_time_bound
        self.block_interval = block_interval

        self.regular_block_delay = 12.5

        self.lambd_without_extra_delay = self.regular_block_delay / block_interval
        self.lambd_with_extra_delay = (
            self.regular_block_delay + withholding_time_bound
        ) / block_interval

    def compute_expectation(self):
        return self.withholding_time_bound / self.block_interval

    def get_block_interval(self):
        return self.block_interval

    def get_withholding_time_bound(self):
        return self.withholding_time_bound

    def get_expectation(self):
        return self.expectation
