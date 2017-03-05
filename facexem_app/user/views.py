from flask import Blueprint, redirect, url_for, request, jsonify, session, g
from flask_login import login_user, logout_user, current_user, login_required
from ..extensions import db, lm
import json
from .models import User
from flask_cors import cross_origin


user = Blueprint('user', __name__, url_prefix='/user')

@user.before_request
def before_request():
    g.user = current_user

@user.route('/create', methods=['POST'])
def create_user():
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
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")

@user.route('/delete', methods=['POST'])
def delete_user():
    data = json.loads(request.data)
    user_id = data['id']
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return 'User with id = '+user_id+' deleted'



@user.route('/getall', methods=['POST'])
def get_users():
    users = User.query.all()
    find = []
    for person in users:
        give = [{'id': person.id,
                'name': person.name,
                 'email': person.email,
                 'token': person.token,
                 'role': person.role}]
        find.append(give)
    return jsonify(find)



@user.route('/login', methods=['POST'])
def login_user():
    if g.user is not None and g.user.is_authenticated:
        return jsonify(result="Success")
    else:
        data = json.loads(request.data)
        email = data['email']
        password = data['pass']
        possible_user = User.query.filter_by(email=email).first()
        if possible_user:
            if possible_user.check_password(password):

                return jsonify(result="Success")
            else:
                return jsonify(result="Error")



@user.route('/getpage', methods=['POST', 'GET'])
@login_required
def get_page():
    return "Ye bro, you're authorized"


@user.route('/logout',  methods=['POST', "GET"])
def logout():
    logout_user()
    return "good by"