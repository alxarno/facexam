from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__, static_folder='.', static_url_path='')
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views
