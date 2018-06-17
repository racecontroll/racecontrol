from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length


class NewDriverForm(FlaskForm):
    """
    Form Builder for creating a new driver
    """
    name = StringField('name',
                       validators=[DataRequired()])
    shortname = StringField('nickname',
                            validators=[DataRequired(),
                                        Length(max=10)])
    # image =


class DriverForm(FlaskForm):
    """
    Form Builder for modifying an already existing driver
    """
    id = IntegerField('id')
    delete = IntegerField('delete')
    name = StringField('name')
    shortname = StringField('nickname')
