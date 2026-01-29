from dash import html, dcc
import plotly.graph_objects as go


# -------------------------------------------------
# Metric tile
# -------------------------------------------------
def metric_block(label, value):
    return html.Div(
        [
            html.Div(label, style={"fontSize": "11px", "color": "#666"}),
            html.Div(value, style={"fontSize": "20px", "fontWeight": "bold"})
        ],
        style={
            "padding": "10px",
            "border": "1px solid #ddd",
            "borderRadius": "6px",
            "minWidth": "120px"
        }
    )


# -------------------------------------------------
# Single signal plot
# -------------------------------------------------
def signal_plot(signal):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=signal.time,
            y=signal.data,
            mode="lines",
            name=signal.name
        )
    )

    fig.update_layout(
        title=signal.name,
        height=280,
        margin=dict(l=40, r=20, t=40, b=30),
        showlegend=False
    )

    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False}
    )


# -------------------------------------------------
# One LH/RH row for a plot type
# -------------------------------------------------
def lh_rh_row(title, lh_signal, rh_signal, metrics):

    def metric_row(side):
        return html.Div(
            [
                metric_block(k, v)
                for k, v in metrics.items()
                if k.startswith(side)
            ],
            style={"display": "flex", "gap": "10px", "marginTop": "5px"}
        )

    return html.Div(
        [
            html.H4(title, style={"marginBottom": "10px"}),

            html.Div(
                [
                    # ---- LH ----
                    html.Div(
                        [
                            html.H5("LH"),
                            signal_plot(lh_signal) if lh_signal else html.Div("No LH data"),
                            metric_row("LH")
                        ],
                        style={"width": "48%"}
                    ),

                    # ---- RH ----
                    html.Div(
                        [
                            html.H5("RH"),
                            signal_plot(rh_signal) if rh_signal else html.Div("No RH data"),
                            metric_row("RH")
                        ],
                        style={"width": "48%"}
                    )
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "marginBottom": "30px"
                }
            )
        ]
    )
