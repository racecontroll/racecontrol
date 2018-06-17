from flask import render_template
from . import blueprint


@blueprint.route("/")
def index():
    """
    Race view
    """
    return render_template("race/race.html",
                           players=[{"shortname": "Player 1"},
                                    {"shortname": "Player 2"}])
