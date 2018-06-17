from flask import current_app
from sqlalchemy.exc import IntegrityError
from . import db


class Driver(db.Model):
    """
    Database entry which contains information about a driver

    :param name: Name
    :param shortname: Nickname
    :param image: Image ID; NOT IMPLEMENTED @TODO
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    shortname = db.Column(db.String(10), unique=True, nullable=False)
    # image = db.Column(db.String(64), nullable=True)

    @staticmethod
    def add_to_db(name, shortname):
        """
        Adds a driver to the database

        :param name: Name
        :param shortname: Nickname
        """

        toadd = Driver(name=name, shortname=shortname)
        try:
            db.session.add(toadd)
            db.session.commit()
            return True

        except IntegrityError as ie:
            current_app.logger.error(str(ie))
            return False

    def __repr__(self):
        """
        :returns: String representation of the driver
        """
        return f"<{self.shortname} - {self.name}>"
