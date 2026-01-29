from dash import Dash
from application.layout import build_layout
from application.callbacks import register_callbacks


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Ride Analysis"
)

app.layout = build_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=False
    )
