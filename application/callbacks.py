from dash import html
from dash.dependencies import Input, Output

from application.data_provider import OAES
from application.components import metric_block, lh_rh_row


def register_callbacks(app):

    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def render_oae(pathname):

        if pathname in (None, "/"):
            return html.Div("Select an OAE from above.")

        oae_name = pathname.replace("/", "")

        if oae_name not in OAES:
            return html.Div(f"Unknown OAE: {oae_name}")

        oae = OAES[oae_name]

        # ===== SUMMARY METRICS =====
        summary = html.Div(
            [
                metric_block(k, v)
                for k, v in oae["summary"].items()
            ],
            style={
                "display": "flex",
                "gap": "15px",
                "marginBottom": "25px"
            }
        )

        # ===== LH / RH ROWS =====
        rows = []

        for plot_name, plot_data in oae["plots"].items():
            rows.append(
                lh_rh_row(
                    plot_name,
                    plot_data.get("LH"),
                    plot_data.get("RH"),
                    plot_data.get("metrics", {})
                )
            )

        return html.Div([summary] + rows)
