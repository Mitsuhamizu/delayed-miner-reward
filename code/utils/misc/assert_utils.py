import numpy as np


def assert_all_non_negative(array):
    for element in array:
        assert element >= 0


def assert_all_non_negative_and_equal_one(probabilities):
    assert_all_non_negative(probabilities)

    np.testing.assert_almost_equal(np.sum(probabilities), 1)
