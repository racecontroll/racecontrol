from flask import render_template, url_for, redirect

from . import blueprint
from ...models import Car
from ...util.database.helper import remove_from_db
from .forms import NewCarForm, DeleteCarForm


@blueprint.route("/")
def index():
    """
    Displays all cars
    """

    cars = Car.query.all()
    return render_template("car/cars.html", cars=cars)


@blueprint.route("/newcar", methods=["GET", "POST"])
def new_car():
    """
    Creates a new car
    """

    form = NewCarForm()
    added_new = False
    if form.validate_on_submit():
        added_new = Car.add_to_db(form.name.data,
                                  form.manufacturer.data,
                                  form.scale.data)
        if not added_new:
            return "@ERROR TODO"
        else:
            # @TODO
            return redirect(url_for(".index"))

    return render_template("car/new_car.html", form=form, added_new=added_new)


@blueprint.route("/profile/<id>", methods=["GET", "POST"])
def profile(id):
    """
    Views the car profile

    :param id: Car database ID
    """

    car = Car.query.filter_by(id=id).first()
    form = DeleteCarForm()
    deleted = False

    if form.validate_on_submit():
        # Delete car
        deleted = remove_from_db(Car, id)

        if deleted:
            return redirect(url_for(".index"))

    return render_template("car/profile.html", car=car, form=form)
