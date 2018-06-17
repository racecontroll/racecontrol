from flask import current_app
from sqlalchemy.exc import IntegrityError
from . import db


class Car(db.Model):
    """
    Database entry for a car

    :param name: Car name
    :param manufacturer: Sar manufacturer
    :scale: Car scale; 1/.. if set to -1 it shows up as "other"
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    manufacturer = db.Column(db.String, nullable=False)
    scale = db.Column(db.Integer, nullable=False)
    # image = db.Column(db.String(64), nullable=True)

    @staticmethod
    def add_to_db(name, manufacturer, scale):
        """
        Adds a car to the database

        :param name: Car name
        :param manufacturer: Sar manufacturer
        :scale: Car scale; 1/.. if set to -1 it shows up as "other"
        """

        # Non supported scale
        if scale not in [-1, 24, 32, 43]:
            return False

        toadd = Car(name=name, manufacturer=manufacturer, scale=scale)

        try:
            db.session.add(toadd)
            db.session.commit()
            return True

        except IntegrityError as ie:
            current_app.logger.error(str(ie))
            return False

    def __repr__(self):
        """
        :returns: String representation of the Car entry
        """
        return f"<{self.name} - {self.manufacturer} - {self.scale}>"
