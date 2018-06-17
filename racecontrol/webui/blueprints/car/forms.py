from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class NewCarForm(FlaskForm):
    """
    Form Builder for creating a new car
    """

    name = StringField('name', validators=[DataRequired()])
    scale = IntegerField('scale', validators=[DataRequired()])
    manufacturer = StringField('manufacturer', validators=[DataRequired()])


class DeleteCarForm(FlaskForm):
    """
    Form Builder for deleting a car, currently used for csrf protection only
    """
    pass
