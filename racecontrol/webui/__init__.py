import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .util.framework.blueprint import register_blueprint
from .util.config.routing import register_initial_redirect


# Database
db = SQLAlchemy()


def get_blueprints():
    """
    :returns: list of blueprints which should be registered
    """
    blueprints = [
        ("core", "/core"),
        ("race", "/race"),
        ("settings", "/settings"),
        ("car", "/car"),
        ("driver", "/driver")
    ]

    for name, target in blueprints:
        yield name, target


def register_blueprints(app):
    """
    Registers a blueprint

    :param app: Flask app
    """
    for name, target in get_blueprints():
        register_blueprint(app, name, target)


def create_app():
    """
    WebUI fabric, initializes the configurations and returns a ready to use
    Flask object

    The configuration file is passed by the environment variable `CONFIG`

    :returns: Ready to use Flask app
    """
    app = Flask(__name__)

    # Import configuration
    # app.config.from_pyfile(os.environ.get("CONFIG", "../config/docker.py"))
    # @TODO
    app.config.from_object("racecontrol.config")

    # Initialize DB
    db.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Register initial redirect
    register_initial_redirect(app)

    return app
