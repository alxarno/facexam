from flask import Blueprint, redirect, url_for, request, jsonify
from ..extensions import db
import json
from .models import User

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/create', methods=['POST'])
def create():
    data = json.loads(request.data)
    # name = data['name']
    email = data['email']
    password = data['pass']
    print(email, password)
    return "Пользователь тут"

@user.route('/getallusers', methods=['POST'])
def getUsers():
    users = User.query.all()
    for person in users:
        name = person.name
        email = person.email
        password = person.password
        give = [{'name':name,
                 'email':email,
                 'pass': password }]
    return jsonify(give)

