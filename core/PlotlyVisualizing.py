import plotly.express as px
from plotly import subplots
import plotly.graph_objs as go


def show_from_df(df):
    fig = subplots.make_subplots(len(df.keys()), 1)
    for i, key in enumerate(df.keys()):
        fig.append_trace(go.Scatter(x=df.index, y=df[key], name='%s history' % key), row=i + 1, col=1)
        fig.update_xaxes(title_text="Date", row=i + 1, col=1)
        fig.update_yaxes(title_text=key, row=i + 1, col=1)

    fig.show()


def show_soil_from_df(df):
    fig = px.scatter(df, x="layer_sym", y="T", animation_frame="t", animation_group='layer_sym')
    fig.show()
