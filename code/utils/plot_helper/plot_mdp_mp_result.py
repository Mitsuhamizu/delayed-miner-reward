import os.path as op
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.append(op.abspath(op.join(__file__, op.pardir, op.pardir)))

from misc.reader import *

mpl.use("tkagg")
alphas = [round((i * 0.05), 2) for i in range(11)]


def remove_odd_xtick(g):
    # iterate over axes of FacetGrid
    for ax in g.axes.flat:
        labels = ax.get_xticklabels()  # get x labels
        for i, l in enumerate(labels):
            if i % 2 != 0:
                labels[i] = ""  # skip even labels
        ax.set_xticklabels(labels)  # set new labels
    return g


def plot_and_save_fig(
    file_path, data, plot_basic_config, sub_fig_classify_criteria, label, sharey
):

    sns.set_theme(style="darkgrid")

    data["γ"] = data["γ"].apply(str)
    data["γ"] = data["γ"].replace("0.0", "0")
    data["γ"] = data["γ"].replace("1.0", "1")

    print(data)

    # if the text is type, just remove it.
    if label == "type":
        data.columns = [n if n != label else "" for n in data.columns]
        label = ""
    g = sns.FacetGrid(
        data,
        col=sub_fig_classify_criteria,
        hue=label,
        legend_out=True,
        hue_kws=dict(
            marker=["o", "v", "+", "x", "*", "p", "1", "2", "8"], linestyle=["--"] * 9
        ),
        sharey=sharey,
    )

    g = g.map_dataframe(
        plt.plot,
        "ρ",
        "extra revenue",
    )

    for ax in g.axes.flat:
        pass
    ax.legend(ncol=2, labelspacing=4, bbox_to_anchor=(-0.2, 1.35))

    plot_basic_config.apply_style(g)
    plt.xticks([i * 0.1 for i in range(6)])
    plt.yticks([-0.05] + [i * 0.05 for i in range(4)])

    plt.savefig(
        file_path,
        bbox_inches="tight",
    )

    plt.clf()


# def convert_raw_data_to_plot_data(
#     data,
# ):
#     plot_data = pd.DataFrame(
#         columns=[
#             "type",
#             "block interval",
#             "withholding time",
#             "gamma",
#             "mining power",
#             "relative revenue",
#         ]
#     )

#     for _, row in data.iterrows():
#         for index in range(len(row["revenue"])):
#             plot_data.loc[plot_data.shape[0]] = [
#                 row["type"],
#                 row["block interval"],
#                 row["withholding time"],
#                 row["gamma"],
#                 alphas[index],
#                 row["revenue"][index] - alphas[index],
#             ]
#     return plot_data


def plot_mdp_mp_result(
    file_paths,
    criteria,
    label,
    plot_basic_config,
    save_path,
    sharey=True,
):

    # load data and merge.
    data = pd.concat(
        [load_data_and_attach_type(file_path_iter) for file_path_iter in file_paths]
    )
    # plot, given the config and text.
    plot_and_save_fig(save_path, data, plot_basic_config, criteria, label, sharey)
