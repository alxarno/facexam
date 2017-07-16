from flask import Flask, jsonify, session, url_for, request, redirect
from .extensions import db, lm
from .user.views import user
from .subject.views import subject
from .author.views import author
from .author.models import Author
from .admin.views import admin
from .achievements.views import achievement
from .user.models import User
from flask_cors import CORS
from .user.constans import ROLES
from config import ADMIN_KEY, AUTHOR_KEY
import json, jwt
from config import SECRET_KEY

app = Flask('Facexem', instance_relative_config=True, static_folder='frontend')
app.register_blueprint(user)
app.register_blueprint(author)
app.register_blueprint(subject)
app.register_blueprint(achievement)
app.register_blueprint(admin)
app.config.from_object('config')
db.app = app
db.init_app(app)
lm.init_app(app)
lm.login_view = 'login'
CORS(app)


def verif_author():
    if 'token' in session:
        token = session['token']
        data_token = jwt.decode(token, SECRET_KEY)
        user_token = data_token['public']
        current_author = User.query.filter_by(token=user_token).first()
        current_author = Author.query.filter_by(user_id=current_author.id).first()
        if current_author:
                return current_author
    return False


@app.route('/login', methods=['GET'])
def login():
    if 'token' in session:
        data_token = jwt.decode(session['token'], SECRET_KEY)
        user_token = data_token['public']
        user = User.query.filter_by(token=user_token).first()
        if user:
            return redirect(url_for('main'))
        else:
            return app.send_static_file('enter/index.html')
    else:
        return app.send_static_file('enter/index.html')



@app.route('/achiev/<smth>')
def achievements(smth):
    return app.send_static_file('other/achievements/'+smth+'.png')


@app.route('/avatars/<smth>')
def avatars(smth):
    return app.send_static_file('other/avatars/'+smth)


@app.route('/task_img/<id>/<name>')
def task_img(name, id):
    return app.send_static_file('other/tasks/'+id+'/'+name+'.png')


@app.route('/bg/<smth>')
def backgrounds(smth):
    return app.send_static_file('other/backgrounds/'+smth)


@app.route('/icon/<smth>')
def icons(smth):
    return app.send_static_file('other/icons&pictures/'+smth+'.svg')


@app.route('/interface/<smth>')
def interface(smth):
    return app.send_static_file('other/interface/'+smth+'.svg')


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


@app.route('/create-profile', methods=['GET'])
def create_profile():
    if 'token' in session:
        print(session['token'])
        data_token = jwt.decode(session['token'], SECRET_KEY)
        user_token = data_token['public']
        user = User.query.filter_by(token=user_token).first()
        if user:
            if user.profile_done == 0:
                return app.send_static_file('create-profile/index.html')
            else:
                return redirect(url_for('main'))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/<smth>',  methods=['GET'])
def somewhere1(smth):
    if 'token' in session:
        data_token = jwt.decode(session['token'], SECRET_KEY)
        user_token = data_token['public']
        user = User.query.filter_by(token=user_token).first()
        if user:
            if user.profile_done == 0:
                return redirect(url_for('create_profile'))
            else:
                return app.send_static_file('user/index.html')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/<smth>/<smth2>',  methods=['GET'])
def somewhere2(smth, smth2):
    if 'token' in session:
        data_token = jwt.decode(session['token'], SECRET_KEY)
        user_token = data_token['public']
        user = User.query.filter_by(token=user_token).first()
        if user:
            if user.profile_done == 0:
                return redirect(url_for('create_profile'))
            else:
                return app.send_static_file('user/index.html')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/mypage',  methods=['GET'])
def main():
    if 'token' in session:
        data_token = jwt.decode(session['token'], SECRET_KEY)
        user_token = data_token['public']
        user = User.query.filter_by(token=user_token).first()
        if user:
            if user.profile_done == 0:
                return redirect(url_for('create_profile'))
            else:
                return app.send_static_file('user/index.html')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/',  methods=['GET'])
def enter():
    if 'token' in session:
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))


@app.route('/task/redactor/<number>',  methods=['GET'])
def redactor_task(number):
    user = verif_author()
    if user:
        return app.send_static_file('redactor/index.html')
    else:
        return redirect(url_for('main'))


@app.route('/achiev',  methods=['GET'])
@app.route('/tasks',  methods=['GET'])
@app.route('/author',  methods=['GET'])
def author_page():
    user = verif_author()
    if user:
        return app.send_static_file('author/index.html')
    else:
        return redirect(url_for('main'))


@app.errorhandler(405)
def page_not_found(error):
    return request.method + " isn't our method", 405


@app.errorhandler(404)
def page_not_found(error):
    return 'Not found', 404


@app.errorhandler(500)
def server_error_page(error):
    return 'Server error', 500
