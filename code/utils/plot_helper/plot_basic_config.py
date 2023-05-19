import copy


class Plot_size:
    def __init__(self, params):
        self.params = params


class Plot_text:
    def __init__(self, labels=dict(), title=None):
        if "x" in labels.keys():
            self.xlabel = labels["x"]
        else:
            self.xlabel = None
        if "y" in labels.keys():
            self.ylabel = labels["y"]
        else:
            self.ylabel = None
        self.title = title

    def set_text(self, labels={}, title=None):
        if "x" in labels.keys():
            self.xlabel = labels["x"]
        else:
            self.xlabel = None
        if "y" in labels.keys():
            self.ylabel = labels["y"]
        else:
            self.ylabel = None
        self.title = title


class Plot_basic_config:
    def __init__(self, params, labels=None, title=None):
        self.size = Plot_size(params)
        self.text = Plot_text(labels, title)

    def apply_size(self, g, type):
        if type == "horizontal":
            for ax in g.axes.flat:
                ax.set_xticklabels(
                    ax.get_xticklabels(),
                    fontdict={"fontsize": self.size.params["tick_text"]},
                )
                ax.set_xlabel(ax.get_xlabel(), fontsize=self.size.params["axis_label"])

                ax.set_title(
                    label=ax.title._text,
                    size=self.size.params["title_text"],
                )

            g.axes.flat[0].set_yticklabels(
                g.axes.flat[0].get_yticklabels(),
                fontdict={"fontsize": self.size.params["tick_text"]},
            )
            g.axes.flat[0].set_ylabel(
                g.axes.flat[0].get_ylabel(), fontsize=self.size.params["axis_label"]
            )
        elif type == "vertical":
            for ax in g.axes.flat:
                ax.set_yticklabels(
                    ax.get_yticklabels(),
                    fontdict={"fontsize": self.size.params["tick_text"]},
                )
                ax.set_ylabel(ax.get_ylabel(), fontsize=self.size.params["axis_label"])

                ax.set_title(
                    label=ax.title._text,
                    size=self.size.params["title_text"],
                )

            g.axes.flat[-1].set_xticklabels(
                g.axes.flat[-1].get_xticklabels(),
                fontdict={"fontsize": self.size.params["tick_text"]},
            )
            g.axes.flat[-1].set_xlabel(
                g.axes.flat[-1].get_xlabel(), fontsize=self.size.params["axis_label"]
            )
            g.axes.flat[-1].set_ylabel("")
            g.axes.flat[0].set_ylabel("")
        # for text in g.legend.texts:
        #     text.set_fontsize(self.size.params["legend_text"])

    def apply_text(self, ax, ignored):

        if self.text.xlabel != None and "x text" not in ignored:
            ax.set(xlabel=self.text.xlabel)
        if self.text.ylabel != None and "y text" not in ignored:
            ax.set(ylabel=self.text.ylabel)
        if self.text.title != None and "title" not in ignored:
            ax.set(title=self.text.title)

    def apply_style(self, g, ignored=[], type="horizontal"):
        self.apply_text(g, ignored)
        self.apply_size(g, type)

    def set_text(self, labels=dict(), title=None):
        self.text.set_text(labels, title)
