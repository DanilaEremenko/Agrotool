import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def show_from_df(df):
    fig, axs = plt.subplots(len(df.keys()))
    for ax, key in zip(axs, df.keys()):
        ax.plot(df[[key]], ".-")
        ax.set_ylabel(key)
        plt.sca(ax)
        plt.xticks(rotation=45)

    fig.show()
