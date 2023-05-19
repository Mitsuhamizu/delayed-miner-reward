import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

mpl.use("tkagg")
sns.set_theme()
sns.set_style("whitegrid")


def plot_frequency_fork(file_name, data, hue, stat, multiple, plot_basic_config):

    ax = sns.histplot(
        data=data,
        stat=stat,
        x="share",
        hue=hue,
        multiple=multiple,
        common_norm=False,
        shrink=0.7,
    )

    ax.legend_.set_title(None)

    plot_basic_config.apply_style(ax)

    plt.savefig(
        file_name,
        bbox_inches="tight",
        pad_inches=0.0,
    )

    plt.clf()


def plot_frequency_time_diff(file_name, data, plot_basic_config):

    ax = sns.histplot(
        data=data,
        shrink=0.7,
    )

    plot_basic_config.apply_style(ax)

    plt.savefig(
        file_name,
        bbox_inches="tight",
        pad_inches=0.0,
    )

    plt.clf()
