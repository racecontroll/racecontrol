from flask import render_template
from . import blueprint


@blueprint.route("/")
def index():
    """
    Main view, No race, just a description
    """
    return render_template("core/index.html")
