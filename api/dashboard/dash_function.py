import dash_html_components as html


def apply_layout(app, layout):
    def serve_layout():
        return html.Div([
            html.Div('1', id='session_id', style={'display': 'none'}), layout
        ], className="container-fluid",
            style=dict(width='100%', position='absolute', left='0'))

    app.layout = serve_layout
