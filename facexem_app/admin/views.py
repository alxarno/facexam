import json

from flask import Blueprint, request, jsonify, session

from ..user.models import User, TestUser
from ..user.constans import ROLES
from ..subject.models import Task
from ..extensions import db
from config import ADMIN_KEY, AUTHOR_KEY

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


def verif_admin():
    data = json.loads(request.data)
    token = data['token']
    current_admin = User.query.filter_by(token=token).first()
    if current_admin:
        if current_admin.role == ROLES['ADMIN']:
            if 'token' in session:
                if session['token'] == token:
                    return True
                else:
                    return False
            else:
                try:
                    user_code = data['code']
                except:
                    return False
                if user_code == ADMIN_KEY:
                    return True
                else:
                    return False
        else:
            return False
    else:
        return False


@admin.route('/info', methods=['POST'])
def info_admin():
    if verif_admin():
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")


@admin.route('/get_all_improved_email', methods=['POST'])
def get_all_improved_email():
    if verif_admin():
        tests = TestUser.query.all()
        find = []
        for person in tests:
            give = [{'id': person.id,
                     'email': person.email,
                     'key': person.key}]
            find.append(give)
        return jsonify(find)
    else:
        return jsonify(result="Error")


@admin.route('/get_all', methods=['POST'])
def get_users():
    if verif_admin():
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
    else:
        return jsonify(result="Error")


@admin.route('/get_task', methods=['POST'])
def get_task():
    if verif_admin():
        data = json.loads(request.data)
        try:
            task_id = data['task_id']
        except:
            return jsonify(result='Error: need task_id')
        task = Task.query.filter_by(id=task_id).first()
        if task:
            return jsonify({'id': task.id,
                            'content': task.content,
                            'answer': task.answer,
                            'description': task.description})
        else:
            return jsonify(result='Error: you are not admin ')


@admin.route('/smth', methods=['POST'])
def smth():
    if verif_admin():
        data = json.loads(request.data)
        token = data['token']
        current_admin = User.query.filter_by(token=token).first()
        current_admin.info_page[0].user_achievements = json.dumps({})
        db.session.commit()
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")

