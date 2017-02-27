from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
app.config.from_object('config')
db = SQLAlchemy(app)
CORS(app)

from app import views
