from flask import render_template, url_for, redirect, abort
from . import blueprint
from ...models import Driver
from ... import db
from ...util.database.helper import remove_from_db
from .forms import NewDriverForm, DriverForm


@blueprint.route("/")
def index():
    """
    List of all drivers
    """
    drivers = Driver.query.all()
    return render_template("driver/drivers.html",
                           drivers=drivers)


@blueprint.route("/newdriver", methods=["GET", "POST"])
def new_driver():
    """
    Adds a new driver
    """

    form = NewDriverForm()
    added_new = False

    if form.validate_on_submit():
        # Add driver to Database
        added_new = Driver.add_to_db(form.name.data, form.shortname.data)
        if not added_new:
            return abort(500)
        else:
            # @TODO add flash
            return redirect(url_for(".index"))

    return render_template("driver/new_driver.html",
                           form=form,
                           added_new=added_new)


@blueprint.route("/profile/<id>", methods=["GET", "POST"])
def profile(id):
    """
    Driver profile with the option to edit it

    :param id: Driver ID
    """
    driver = Driver.query.filter_by(id=id).first()
    form = DriverForm()

    if form.validate_on_submit():
        # Check if the profile should be deleted
        if form.delete.data == 1:
            remove_from_db(Driver, id)
            return redirect(url_for(".index"))
        else:
            driver.name = form.name.data
            driver.shortname = form.shortname.data
            db.session.commit()

    return render_template("/driver/profile.html",
                           form=form,
                           driver=driver)
