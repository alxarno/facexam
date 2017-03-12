from flask import Flask, jsonify, session, url_for, request
from .extensions import db, lm
from .user.views import user
from .subject.views import subject
from flask_cors import CORS

app = Flask('Facexem', instance_relative_config=True, static_folder='frontend')

app.register_blueprint(user)
app.register_blueprint(subject)
app.config.from_object('config')
db.app = app
db.init_app(app)
lm.init_app(app)
lm.login_view = 'login'
CORS(app)


@app.route('/login')
def login():
    if 'token' in session:
        return session['token']
    else:
        return app.send_static_file('enter/index.html')


@app.errorhandler(405)
def page_not_found(error):
    return request.method + " isn't our method", 405


@app.errorhandler(404)
def page_not_found(error):
    return 'Not found', 404


@app.errorhandler(500)
def server_error_page(error):
    return 'Server error', 500
