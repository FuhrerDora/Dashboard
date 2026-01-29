from dash import html, dcc
from application.data_provider import OAES


def build_layout():
    return html.Div([

        dcc.Location(id="url"),

        html.H1("Vehicle Ride Analysis Dashboard"),
        html.Hr(),

        html.Div(
            "LH / RH comparison across Operating Analysis Events (OAEs)",
            style={"marginBottom": "10px"}
        ),

        # ---- DTYPE NAVIGATION ----
        html.Div(
            [
                dcc.Link(
                    dtype,
                    href=f"/{dtype}",
                    style={"marginRight": "20px", "fontWeight": "bold"}
                )
                for dtype in sorted(OAES.keys())
            ],
            style={"marginBottom": "20px"}
        ),

        html.Div(id="page-content")
    ])
