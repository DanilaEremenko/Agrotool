from plotly import subplots
import plotly.graph_objs as go


def show_from_df(df):
    fig = subplots.make_subplots(4, 1, subplot_titles=('T History', 'Prec History', 'Radiation', 'SumSnow'), )
    for i, key in enumerate(["T", "Prec", "Rad", "SumSnow"]):
        fig.append_trace(go.Scatter(x=df["Date"], y=df[key]),
                         row=i + 1, col=1)
        fig.update_xaxes(title_text="Date", row=i + 1, col=1)
        fig.update_yaxes(title_text="T", row=i + 1, col=1)

    fig.show()
