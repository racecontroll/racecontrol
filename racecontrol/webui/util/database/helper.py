from ... import db


def remove_from_db(db_object, id):
    """
    Removes an entry from the database

    :param db_object: SQLAlchemy Database Object
    :param id: Id which should be removed
    :returns: True if successfull
    """
    todel = db_object.query.filter_by(id=id).first()
    if todel:
        db.session.delete(todel)
        db.session.commit()
        return True
    return False
