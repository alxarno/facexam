from flask import Flask, jsonify
from .extensions import db, lm
from .user.views import user
from flask_cors import CORS

app = Flask('Facexem', instance_relative_config=True)
app.register_blueprint(user)
app.config.from_object('config')
db.app = app
db.init_app(app)
lm.init_app(app)
lm.login_view = 'login'
CORS(app)


@app.route('/login')
def login():
        return "It's may be your's login page"

@app.errorhandler(404)
def page_not_found(error):
        return 'Not found', 404



@app.errorhandler(500)
def server_error_page(error):
        return 'Server error', 500
