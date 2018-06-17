# Temporary solution!!!
import os

INITIAL_REDIRECT = "/core"
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SECRET_KEY = 00000000000000000000000000000000
SECRET_KEY = 'racecontroll-webui@development'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' \
                          + os.path.join(os.getcwd(), '../db-dev.sqlite3')
