from dash import html, dcc
from application.data_provider import OAES


def build_layout():
    return html.Div([

        # Needed for URL routing
        dcc.Location(id="url"),

        # ===== HEADER =====
        html.Div(
            "Vehicle Ride Analysis Dashboard",
            style={
                "fontSize": "28px",
                "fontWeight": "bold",
                "padding": "12px",
                "borderBottom": "2px solid #333"
            }
        ),

        # ===== DESCRIPTION =====
        html.Div(
            "LH / RH comparison across Operating Analysis Events (OAEs)",
            style={
                "padding": "10px",
                "color": "#444",
                "fontSize": "14px"
            }
        ),

        # ===== OAE SELECTOR =====
        html.Div(
            [
                dcc.Link(
                    oae_name,
                    href=f"/{oae_name}",
                    style={
                        "marginRight": "20px",
                        "fontWeight": "bold",
                        "textDecoration": "none"
                    }
                )
                for oae_name in OAES.keys()
            ],
            style={
                "padding": "10px",
                "borderBottom": "1px solid #ddd"
            }
        ),

        # ===== DYNAMIC PAGE CONTENT =====
        html.Div(
            id="page-content",
            style={"padding": "15px"}
        )
    ])
