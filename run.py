import sys
from Engine import models
from flask import Flask, abort, redirect, url_for, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

import time

app = Flask(__name__, static_folder='.', static_url_path='')
app.config.from_object('config')
db = SQLAlchemy(app)
db.create_all()
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
migrate = Migrate(app, db)

admin = models.User('admin', 'admin@example.com')
guest = models.User('guest', 'guest@example.com')
db.session.add(admin)
db.session.add(guest)
db.session.commit()

@app.route('/')
def home():
    return  redirect(url_for('login'))

@app.route('/api/users')
def user():
    users = models.User.query.all()
    return jsonify(users)

@app.route('/mypage')
def userpage():
    return app.send_static_file('Front-end/EnterpriseUser/index.html')

@app.route('/<subject>')
def subjectpage(subject):
    return app.send_static_file('Front-end/EnterpriseUser/index.html')

@app.route('/<subject>/lection/<int:lessonid>')
@app.route('/<subject>/lection/')
@app.route('/<subject>/lection')
@app.route('/<subject>/test/<int:lessonid>')
@app.route('/<subject>/test/')
@app.route('/<subject>/test')
def lectionsPage(subject, lessonid=None):
    return redirect(url_for('subjectpage', subject=subject))


@app.route('/login')
def login():
    return app.send_static_file('Front-end/EnterpriseLogin/index.html')

@app.route('/api/enter')
def enter():
    loginUser = request.args.get('login', 0, type=str)
    passwordUser = request.args.get('pass', 0, type=str)
    if(loginUser=='jesus' and passwordUser == '1111'):
        return jsonify(result='/mypage')
    else:
        return jsonify(result='Error')



@app.route('/redactor')
def redactor():
    return redirect(url_for('static', filename='Front-end/EnterpriseUser/index.html'))


@app.route('/api/test', methods=['GET', 'OPTIONS'])
@cross_origin()
def test():
    jesus = "Congratulations, api is work @facexem_api. Time is ("+time.ctime(time.time())+')'
    return jsonify(jesus)

app.run(port=9999, debug=True)