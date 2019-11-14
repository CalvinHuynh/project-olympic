
def apply_layout(app, layout):
    def serve_layout():
        app.config.suppress_callback_exceptions = True
        app.layout = serve_layout
