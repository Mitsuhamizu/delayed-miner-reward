import matplotlib.pyplot as plt
import matplotlib.text as text
import numpy as np
import seaborn as sns

# The function plot the data in daraframe.
# The data frame should have following columns
# 1. γ, 2. ρ, 3. Extra revenue, 4. expectation


def rule_odd_label_out(labels):
    for i, l in enumerate(labels):
        if i % 2 != 0:
            labels[i] = ""  # skip even labels
    return labels


def plot_revenue_diff_expectation(file_paths, data, plot_basic_config, data_src):

    # if the text is type, just remove it.
    data["γ"] = data["γ"].apply(str)
    data["γ"] = data["γ"].replace("0.0", "0")
    data["γ"] = data["γ"].replace("1.0", "1")

    data.rename(columns={"extra revenue": "Extra revenue"}, inplace=True)

    if data_src == "MDP":
        data["Extra revenue"] *= 100
        data["λ"] = data["λ"].apply(str)
        data["λ"] = data["λ"].replace("0.03333", r"$\frac{1}{30}$")
        data["λ"] = data["λ"].replace("1.0", "1")
        data["λ"] = data["λ"].replace("5.0", "5")
        data["λ"] = data["λ"].replace("10.0", "10")
        sns.set(style="darkgrid", rc={"figure.figsize": (10, 10)})
    if data_src == "MP":
        data["Extra revenue"] *= 1000
        sns.set(rc={"figure.figsize": (10, 10)})
    g = sns.FacetGrid(
        data,
        col="γ",
        hue="λ",
        legend_out=True,
        hue_kws=dict(
            marker=["o", "v", "+", "x", "*", "p", "1", "2", "8"], linestyle=["--"] * 9
        ),
        sharey=True,
    )
    g = g.map_dataframe(
        plt.plot,
        "ρ",
        "Extra revenue",
    )

    # if data_src == "MP":
    #     g.set(yticks=[i * 1 for i in range(4)] + [i * -1 for i in range(4)])
    # elif data_src == "MDP":
    #     g.set(xticks=[i * 0.1 for i in range(6)])
    #     g.set(yticks=[i * 10 for i in range(6)])

    for ax in g.axes.flat:
        x_labels = ax.get_xticklabels()  # get x labels
        x_ticks = ax.get_xticks()

        if data_src == "MDP":
            ax.set_xlim(-0.02, 0.5)
            ax.set_ylim(-1, 30)
            plt.subplots_adjust(wspace=0.15)
            x_ticks = np.array([i * 0.05 for i in range(11)])
            x_labels = [
                text.Text(i * 0.05, 0, "{:.1f}".format(i * 0.05)) for i in range(11)
            ]
            x_labels = rule_odd_label_out(x_labels)
        if data_src == "MP":

            plt.subplots_adjust(wspace=0.15)
            ax.set_xlim(-0.35, 10.3)
            x_labels = rule_odd_label_out(x_labels)
            x_ticks = np.append(x_ticks, 10)
            x_labels.append(text.Text(10, 0, "0.5"))
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(
            x_labels, fontdict={"fontsize": plot_basic_config.size.params["tick_text"]}
        )

    if data_src == "MP":
        legend_position = (0.65, 1.5)

    elif data_src == "MDP":
        legend_position = (0.14, 1.56)
        g.axes.flat[0].set(ylabel="Extra Revenue [%]")

    h, l = ax.get_legend_handles_labels()
    ph = [plt.plot([], marker="", ls="")[0]]
    handles = ph + h
    labels = ["λ:"] + l

    leg = ax.legend(
        handles,
        labels,
        ncol=5,
        labelspacing=0.5,
        columnspacing=0.8,
        bbox_to_anchor=legend_position,
        fontsize=plot_basic_config.size.params["legend_text"],
    )
    for vpack in leg._legend_handle_box.get_children()[:1]:
        for hpack in vpack.get_children():
            hpack.get_children()[0].set_width(0)

    plot_basic_config.apply_style(g)

    for file_path in file_paths:
        plt.savefig(
            file_path,
            bbox_inches="tight",
            pad_inches=0.0,
        )
    plt.clf()
