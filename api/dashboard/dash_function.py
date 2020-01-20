import dash_html_components as html
import dash_bootstrap_components as dbc


def apply_layout(app, layout):
    def serve_layout():
        return dbc.Container([
            html.Div('1', id='session_id', style={'display': 'none'}), layout
        ], fluid=True)

    app.layout = serve_layout
