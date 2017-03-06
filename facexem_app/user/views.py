from flask import Blueprint, redirect, url_for, request, jsonify, session, g
from ..extensions import db, lm
import json
from .models import User, TestUser

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/create', methods=['POST'])
def create_user():
    data = json.loads(request.data)
    email = data['email']
    current_email = User.query.filter_by(email=email).first()
    if current_email is None:
        new_test_user = TestUser(email)
        db.session.add(new_test_user)
        db.session.commit()
        print(new_test_user.key)
        return jsonify(result="Prove email")
    else:
        return jsonify(result="Error")


@user.route('/prove_email', methods=['POST'])
def prove_email():
    data = json.loads(request.data)
    email = data['email']
    name = data['name']
    key = data['key']
    password = data['pass']
    created_user = TestUser.query.filter_by(key=key).first()
    if created_user:
        if created_user.email == email:
            new_user = User(name, password, email)
            db.session.add(new_user)
            token = new_user.token
            session['token'] = token
            session.pop('test_email', None)
            TestUser.query.filter_by(email=email).delete()
            db.session.commit()
            print("User " + name + " is created")
            return jsonify(result="Success")
        else:
            return jsonify(result='Bad email')
    else:
        return jsonify(result="Bad key")


@user.route('/get_all_test', methods=['POST'])
def get_test():
    tests = TestUser.query.all()
    find = []
    for person in tests:
        give = [{'id': person.id,
                 'email': person.email,
                 'key': person.key}]
        find.append(give)
    return jsonify(find)


@user.route('/delete_test', methods=['POST'])
def delete_test():
    data = json.loads(request.data)
    test_id = data['id']
    current_test = TestUser.query.filter_by(id=test_id).first()
    if current_test:
        TestUser.query.filter_by(id=test_id).delete()
        db.session.commit()
        return 'Test user with id = ' + test_id + ' deleted'
    else:
        return "Test user with id = " + test_id + " haven't"


@user.route('/delete', methods=['POST'])
def delete_user():
    data = json.loads(request.data)
    user_id = data['id']
    current_user = User.query.filter_by(id=user_id).first()
    if current_user:
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
        return 'User with id = ' + user_id + ' deleted'
    else:
        return "User with id = " + user_id + " haven't"


@user.route('/get_all', methods=['POST'])
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


@user.route('/get_token', methods=['POST'])
def get_token():
    if 'token' in session:
        return session['token']
    else:
        return redirect(url_for('login'))


@user.route('/login', methods=['POST'])
def login_user():
    if 'token' in session:
        return jsonify(result="Success")
    else:
        data = json.loads(request.data)
        email = data['email']
        password = data['pass']
        possible_user = User.query.filter_by(email=email).first()
        if possible_user:
            if possible_user.check_password(password):
                token = possible_user.token
                session['token'] = token
                return jsonify(result="Success")
            else:
                return jsonify(result="Error")


@user.route('/logout', methods=['POST', "GET"])
def logout():
    session.pop('token', None)
    return redirect(url_for('login'))
