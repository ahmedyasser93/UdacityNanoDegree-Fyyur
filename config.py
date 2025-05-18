from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
# Initialize the app and configure extensions here
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:910172@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the db object
db = SQLAlchemy(app)

# Initialize Migrate and Moment extensions
migrate = Migrate(app, db)
moment = Moment(app)

# Set the csrf token for Flask-WTF if needed
app.config['WTF_CSRF_ENABLED'] = False

