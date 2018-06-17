from flask import render_template
from . import blueprint
from ...models import Driver, Car


@blueprint.route("/")
def index():
    """
    Settings view
    """
    return render_template("settings/index.html",
                           car_count=len(Car.query.all()),
                           driver_count=len(Driver.query.all()))
