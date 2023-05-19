from cgitb import handler
from re import X
from turtle import title

import matplotlib.pyplot as plt
import matplotlib.text as text
import numpy as np
import seaborn as sns

# The function plot the data in daraframe.
# The data frame should have following columns
# 1. γ, 2. ρ, 3. extra revenue, 4. expectation


def rule_odd_label_out(labels):
    for i, l in enumerate(labels):
        if i % 2 != 0:
            labels[i] = ""  # skip even labels
    return labels


def plot_delay_revenue_subfig(file_paths, data, plot_basic_config):
    sns.set_theme(style="darkgrid")
    # if the text is type, just remove it.
    data["γ"] = data["γ"].apply(str)
    data["γ"] = data["γ"].replace("0.0", "0")
    data["γ"] = data["γ"].replace("1.0", "1")

    g = sns.FacetGrid(
        data,
        col="γ",
        hue="ρ",
        legend_out=True,
        hue_kws=dict(
            marker=["o", "v", "+", "x", "*", "p", "1", "2", "8"], linestyle=["--"] * 9
        ),
        sharey=True,
    )
    g = g.map_dataframe(
        plt.plot,
        "D (s)",
        "Extra revenue",
    )

    print(data.dtypes)
    # g.set(xticks=[i * 0.1 for i in range(6)])
    # g.set(yticks=[i * 0.1 for i in range(6)])

    for ax in g.axes.flat:
        ax.set_xlim(-0.5, 12.5)
        x_labels = ax.get_xticklabels()  # get x labels
        x_ticks = ax.get_xticks()

        x_ticks = np.array([i for i in range(0, 15, 3)])
        x_labels = [text.Text(i, 0, "{}".format(i)) for i in x_ticks]
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)

    plt.subplots_adjust(wspace=0.15)
    legend_position = (0.5, 1.4)

    h, l = ax.get_legend_handles_labels()
    ph = [plt.plot([], marker="", ls="")[0]]
    handles = ph + h
    labels = ["Mining power:"] + l

    plt.legend(
        handles, labels, ncol=5, labelspacing=0.5, bbox_to_anchor=legend_position
    )

    plot_basic_config.apply_style(g)

    for file_path in file_paths:
        plt.savefig(
            file_path,
            bbox_inches="tight",
            pad_inches=0.0,
        )
    plt.clf()
