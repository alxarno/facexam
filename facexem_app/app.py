from flask import Flask, jsonify, session, url_for, request
from .extensions import db, lm
from .user.views import user
from .subject.views import subject
from .admin.views import admin
from .achievements.views import achievement
from flask_cors import CORS

app = Flask('Facexem', instance_relative_config=True, static_folder='frontend')

app.register_blueprint(user)
app.register_blueprint(subject)
app.register_blueprint(achievement)
app.register_blueprint(admin)
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


@app.route('/bg/<smth>')
def backgrounds(smth):
    return app.send_static_file('other/backgrounds/'+smth+'.jpg')


@app.route('/icon/<smth>')
def icons(smth):
    return app.send_static_file('other/icons&pictures/'+smth+'.svg')


@app.route('/subject_pic/<smth>')
def subject_pic(smth):
    return app.send_static_file('other/subjects_pic/'+smth+'.png')


@app.route('/front/css')
def get_styles():
    return app.send_static_file('user/static/css/enter.css')


@app.route('/front/js')
def get_javascript():
    return app.send_static_file('user/static/js/enter.js')


@app.route('/front/smoth')
def get_smoth():
    return app.send_static_file('user/smoth.js')


@app.route('/mypage')
@app.route('/')
def main():
    if 'token' in session:
        return app.send_static_file('user/index.html')
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
