import itertools
import os.path as op
import sys

import pandas as pd

sys.path.append(op.abspath(op.join(__file__, op.pardir)))
from mp_classes.adversary_setting import *
from mp_classes.withholding_mp_model import *
from mp_classes.withholding_setting import *
from mp_parameters import *

if __name__ == "__main__":
    home_dir = op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir))
    for alpha_iter, gamma_iter in itertools.product(alphas, gammas):
        adversary_settings.append(Adversary_setting(alpha_iter, gamma_iter))

    for withholding_setting_iter in withholding_settings:
        result = pd.DataFrame(
            columns=alphas,
            index=gammas,
        )
        for adversary_setting_iter in adversary_settings:
            # get probability
            withholding_mp_iter = Withholding_mp(
                adversary_setting_iter, withholding_setting_iter
            )
            # get fraction of reward
            result = withholding_mp_iter.put_relative_revenue_into_dataframe(result)
        result.to_csv(
            home_dir
            + "/data/mp/mp_{:.5f}.csv".format(
                round(withholding_setting_iter.get_expectation(), 5)
            ),
            encoding="utf-8",
        )
