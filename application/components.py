from dash import html, dcc
import plotly.graph_objects as go


def overlay_plot(cell, title):
    """
    cell = { "ADAMS": Signal, "MV": Signal }
    """

    if not cell:
        return html.Div("No data")

    fig = go.Figure()

    for sim_name, sig in cell.items():
        fig.add_trace(
            go.Scatter(
                x=sig.time,
                y=sig.data,
                mode="lines",
                name=sim_name,
                line=dict(
                    dash="solid" if sim_name == "ADAMS" else "dash"
                )
            )
        )

    fig.update_layout(
        title=title,
        height=250,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h")
    )

    return dcc.Graph(figure=fig)


def lh_rh_row(signal_name, front_lh, front_rh, rear_lh, rear_rh):

    return html.Div(
        [
            html.H3(signal_name),

            html.H4("Front"),
            html.Div(
                [
                    html.Div(
                        [html.H5("LH"), overlay_plot(front_lh, "Front LH")],
                        style={"width": "48%"}
                    ),
                    html.Div(
                        [html.H5("RH"), overlay_plot(front_rh, "Front RH")],
                        style={"width": "48%"}
                    ),
                ],
                style={"display": "flex", "justifyContent": "space-between"}
            ),

            html.H4("Rear"),
            html.Div(
                [
                    html.Div(
                        [html.H5("LH"), overlay_plot(rear_lh, "Rear LH")],
                        style={"width": "48%"}
                    ),
                    html.Div(
                        [html.H5("RH"), overlay_plot(rear_rh, "Rear RH")],
                        style={"width": "48%"}
                    ),
                ],
                style={"display": "flex", "justifyContent": "space-between"}
            ),

            html.Hr()
        ]
    )
