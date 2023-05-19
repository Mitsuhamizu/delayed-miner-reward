import csv
import os.path as op
import sys

from pyparsing import alphas

sys.path.append(op.abspath(op.join(__file__, op.pardir, op.pardir)))
import pandas as pd

# from mdp.setting import *


def read_decisions(file):

    with open(
        file,
        "r",
    ) as file:
        reader = csv.reader(file)
        for row in reader:
            actions = [int(action_iter) for action_iter in row]
            break
    return actions


# Load the data and rephrase it into following format
# 1. adversary's hashrate ρ, 2. the propagation parameter γ, 3. the extra revenue
def load_data(file_path):
    data_loaded = pd.read_csv(
        file_path,
        index_col=0,
    )
    rhos = list(data_loaded.columns.values)
    data_loaded.index.name = "γ"
    data_loaded.reset_index(level=0, inplace=True)

    data_loaded = pd.melt(
        data_loaded,
        id_vars=["γ"],
        value_vars=rhos,
        var_name="ρ",
        value_name="extra revenue",
    )

    return data_loaded


def load_data_and_attach_type(file_path):
    file_name = op.basename(file_path)
    data = load_data(file_path)
    data["ρ"] = data["ρ"].astype(float)
    if "mp" in file_name:
        data["type"] = "mp"
    elif "mdp" in file_name:
        data["type"] = "mdp"
        data["extra revenue"] = data["extra revenue"] - data["ρ"]
    return data
