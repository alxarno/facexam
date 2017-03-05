from flask import Blueprint, redirect, url_for, request, jsonify, session, g
from flask_login import login_user, logout_user, current_user, login_required
from ..extensions import db, lm
import json
from .models import User

user = Blueprint('user', __name__, url_prefix='/user')

@user.before_request
def before_request():
    g.user = current_user

@user.route('/create', methods=['POST'])
def create():
    data = json.loads(request.data)
    name = data['name']
    email = data['email']
    password = data['pass']
    new_user = User(name, password, email)
    # Check for duplicates and creating
    if User.query.filter_by(email=email).first() is None:
        db.session.add(new_user)
        db.session.commit()
        print("User "+name+" is created")
        return "1"
    else:
        return "0"



@user.route('/getall', methods=['POST'])
def getUsers():
    users = User.query.all()
    find=[]
    for person in users:
        give = [{'id': person.id,
                'name': person.name,
                 'email': person.email,
                 'pass': person.pw_hash,
                 'role': person.role}]
        find.append(give)
    return jsonify(find)



@user.route('/login', methods=['POST'])
def loginUser():
    if g.user is not None and g.user.is_authenticated:
        print(g.user)
        return 'Hello'
    else:
        data = json.loads(request.data)
        email = data['email']
        password = data['pass']
        possible_user = User.query.filter_by(email=email).first()
        if possible_user:
            if possible_user.check_password(password):
                session['remember_me'] = possible_user.get_id
                remember_me = session['remember_me']
                session.pop('remember_me', None)
                login_user(possible_user, remember=remember_me)
                return "Success"
            else:
                return "Fail"



@user.route('/getpage', methods=['POST', 'GET'])
@login_required
def getpage():
    return "Ye bro, you're authorized"


@user.route('/logout',  methods=['POST'])
def logout():
    logout_user()
    return "good by"