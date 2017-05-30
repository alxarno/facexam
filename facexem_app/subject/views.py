from flask import Blueprint, jsonify, request, session
from ..extensions import db
import json
from .models import Subject, Task, Challenge
from ..user.models import User
from ..user.constans import ROLES
from ..author.models import Author
from ..admin.models import Admin
from config import ADMIN_KEY, AUTHOR_KEY

subject = Blueprint('subject', __name__, url_prefix='/api/subject')


def verif_author():
    try:
        data = json.loads(request.data)
        token = data['token']
        current_author = Author.query.filter_by(token=token).first()
        if current_author:
            if 'token' in session:
                if session['token'] == token:
                    return current_author
                else:
                    return False
        else:
            current_admin = Admin.query.filter_by(token=token).first()
            if current_admin:
                return current_admin
                # print(session['admin_token'])
                # if 'admin_token' in session:
                #     if session['admin_token'] == token:
                #         return current_admin
                #     else:
                #         return False
    except:
        return False


@subject.route('/get_info', methods=['POST'])
def get_info():
    if verif_author():
        return jsonify(result='yes')
    else:
        return jsonify(result='error')


@subject.route('/get_subjects', methods=['POST'])
def get_subjects():
    if verif_author():
        subjects = Subject.query.all()
        result = []
        for sub in subjects:
            result.append({'name': sub.name, 'codename': sub.codename})
        return jsonify(result)
    else:
        return jsonify(result='Error')


@subject.route('/create_subject', methods=['POST'])
def create_subject():
    if verif_author():
        try:
            data = json.loads(request.data)
            name = data['name']
            codename = data['codename']
        except:
            return jsonify(result='error')
        current_subject = Subject.query.filter_by(codename=codename).first()
        if current_subject is None:
            s = Subject(name=name, access=0, codename=codename)
            db.session.add(s)
            db.session.commit()
            return jsonify(result='Success')
        else:
            return jsonify(result='Error: codename is already exist')
    else:
        return jsonify(result='error')


@subject.route('/get_tasks', methods=['POST'])
def get_tasks():
    if verif_author():
        try:
            data = json.loads(request.data)
            subject_code_name = data['subject_codename']
        except:
            return jsonify(result="Error")
        current_subject = Subject.query.filter_by(codename=subject_code_name).first()
        if current_subject:
            tasks = current_subject.tasks
            final = []
            for task in tasks:
                final.append({'id': task.id, 'number': task.number})
            return jsonify(final)
    else:
        return jsonify(result='Error')


@subject.route('/create_task', methods=['POST'])
def create_task():
    if verif_author():
        try:
            data = json.loads(request.data)
            subject_codename = data['subject_codename']
            task_number = data['task_number']
            content = data['content']
            answer = data['answer']
            description = data['description']
        except:
            return jsonify(result='Error')
        current_subject = Subject.query.filter_by(codename=subject_codename).first()
        if current_subject:
            task = Task(number=task_number, content=json.dumps(content), answer=json.dumps(answer),\
                        description=json.dumps(description), subject=current_subject)
            db.session.add(task)
            db.session.commit()
            return jsonify(result="Success")
        else:
            return jsonify(result="Error")
    else:
        return jsonify(result='Error')


@subject.route('/delete_task', methods=['POST'])
def delete_task():
    if verif_author():
        try:
            data = json.loads(request.data)
            task_id = data['task_id']
        except:
            return jsonify(result='Error')
        u = Task.query.filter_by(id=task_id).first()
        if u:
            db.session.delete(u)
            db.session.commit()
            return jsonify(result='Success')
        else:
            return jsonify(result='Error: this task havent')
    else:
        return jsonify(result='Error')


@subject.route('/create_challenge', methods=['POST'])
def create_challenge():
    if verif_author():
        data = json.loads(request.data)
        try:
            subject_codename = data['subject_codename']
            type = data['type']
            condition = data['condition']
            hard = data['hard']
            prize = data['prize']
            max = data['max']
            content = data['content']
        except:
            return jsonify(result='Error')
        subject = Subject.query.filter_by(codename=subject_codename).first()
        if subject:
            challenge = Challenge(content=content, type=type, max=max, prize=prize, level_hard=hard, \
                                  condition=json.dumps(condition), subject=subject)
            db.session.add(challenge)
            db.session.commit()
            return jsonify(result='Success')
        else:
            return jsonify(result='Error')
    else:
        return jsonify(result='Error')