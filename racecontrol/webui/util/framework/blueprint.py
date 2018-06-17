from importlib import import_module
from flask import Blueprint, Flask


def create_blueprint(name: str, import_name: str):
    """
    Helper for creating a blueprint

    :param name: Name of the blueprint
    :param import_name: Import name, should be `__name__` in most cases
    :returns: Blueprint
    """

    return Blueprint(name,
                     import_name,
                     static_folder="static",
                     template_folder="templates")


def register_blueprint(app: Flask, name: str, url_prefix: str):
    """
    Registers a blueprint to a Flask application

    :param app: Flask app
    :param name: Name of the blueprint, import path is automatically determined
    :param url_prefix: URL prefix to which the blueprint should be registered
    """
    blueprint = getattr(import_module(
        f"app.blueprints.{name}"), "blueprint")

    if app.config["DEBUG"]:
        app.logger.debug(
            f"Registering blueprint {name} to prefix {url_prefix}")

    app.register_blueprint(blueprint, url_prefix=url_prefix)
