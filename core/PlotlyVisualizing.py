from plotly import subplots
import plotly.graph_objs as go


def show_from_df(df):
    fig = subplots.make_subplots(3, 1, subplot_titles=('T History', 'Prec History', 'Radiation'), )

    fig.append_trace(go.Scatter(x=df["Date"], y=df["T"]),
                     row=1, col=1)
    fig.append_trace(go.Scatter(x=df["Date"], y=df["Prec"]),
                     row=2, col=1)
    fig.append_trace(go.Scatter(x=df["Date"], y=df['Rad']),
                     row=3, col=1)

    # Update xaxis properties
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=1)

    # Update yaxis properties
    fig.update_yaxes(title_text="T", row=1, col=1)
    fig.update_yaxes(title_text="R(mm)", row=2, col=1)
    fig.update_yaxes(title_text="K", row=3, col=1)

    fig.show()
