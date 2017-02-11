import sys
from flask import Flask
from flask import jsonify
from flask import abort, redirect, url_for, request
from flask_cors import CORS, cross_origin
import time

app = Flask(__name__, static_folder='.', static_url_path='')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def home():
    return  redirect(url_for('login'))



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
    return jsonify(result=loginUser+passwordUser)


@app.route('/redactor')
def redactor():
    return redirect(url_for('static', filename='Front-end/EnterpriseUser/index.html'))


@app.route('/api/test', methods=['GET', 'OPTIONS'])
@cross_origin()
def test():
    jesus = "Congratulations, api is work @facexem_api. Time is ("+time.ctime(time.time())+')'
    return jsonify(jesus)

app.run(port=9999, debug=True)