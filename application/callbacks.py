from dash import html
from dash.dependencies import Input, Output
from application.data_provider import OAES
from application.components import lh_rh_row


def register_callbacks(app):

    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def render_dtype_page(pathname):

        if not pathname or pathname == "/":
            return html.Div("Select an OAE from above.")

        dtype = pathname.strip("/")

        if dtype not in OAES:
            return html.Div(f"Unknown OAE: {dtype}")

        rows = []

        for signal_name, block in OAES[dtype].items():
            rows.append(
                lh_rh_row(
                    signal_name,
                    block["Front"]["LH"],
                    block["Front"]["RH"],
                    block["Rear"]["LH"],
                    block["Rear"]["RH"],
                )
            )

        return html.Div(rows)
