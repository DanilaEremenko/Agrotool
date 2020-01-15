import matplotlib.pyplot as plt


def show_all_days(df):
    df = df.set_index("Date")

    fig, axs = plt.subplots(3)
    for ax, key in zip(axs, ["T", "Prec", "Rad"]):
        ax.plot(df[[key]], ".-")
        ax.set_ylabel(key)
        plt.sca(ax)
        plt.xticks(rotation=45)
    fig.show()
