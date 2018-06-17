from flask import Flask, redirect


def register_initial_redirect(app: Flask):
    """
    Registers the initial redirect for a flask app based on its configuration
    file. It looks for `INITIAL_REDIRECT`

    :param app: Flask app
    """

    if "INITIAL_REDIRECT" in app.config.keys():

        if app.config["DEBUG"]:
            app.logger.debug(
                f"Initial redirect to {app.config['INITIAL_REDIRECT']}")

        @app.route("/")
        def initial_redirect():
            return redirect(app.config["INITIAL_REDIRECT"])
