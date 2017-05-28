import json
import time
import datetime
import random


from flask import Blueprint, request, jsonify, session

from ..user.models import User, TestUser, UserSubjects
from ..user.constans import ROLES
from ..subject.models import Task, Subject
from ..extensions import db
from .models import Admin
from config import ADMIN_KEY, AUTHOR_KEY

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


def verif_admin():
    data = json.loads(request.data)
    token = data['token']
    current_admin = Admin.query.filter_by(token=token).first()
    if current_admin:
        if 'token' in session:
            if session['token'] == token:
                return current_admin
    else:
        return False


@admin.route('/info', methods=['POST'])
def info_admin():
    if verif_admin():
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")


@admin.route('/login', methods=['POST'])
def login():
    try:
        data = json.loads(request.data)
        email = data['email']
        password = data['pass']
        secret_key = data['key']
    except:
        return jsonify(result='Error')
    admin = Admin.query.filter_by(email=email).first()
    if admin.check_password(password):
        if secret_key == ADMIN_KEY:
            session['admin_token'] = admin.token
            return jsonify(admin.token)
    else:
        return jsonify(result='Error')


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
        subject = data['subject']
        now_time = time.localtime()
        now_date = datetime.date(now_time.tm_year, now_time.tm_mon, now_time.tm_mday)
        # creating array with last 7 days dates
        dates = []
        final = {}
        i = 6
        while i >= 0:
            date = now_date - datetime.timedelta(days=i)
            dates.append(str(date))
            i -= 1
        for i in dates:
            final[i] = random.randint(0, 100)
        current_admin = User.query.filter_by(token=token).first()
        real_subjects = current_admin.info_subjects
        r_subject = 0
        for j in real_subjects:
            if j.subject_codename == subject:
                r_subject = j
        sub = UserSubjects.query.filter_by(id=r_subject.id).first()
        sub.activity = json.dumps(final)
        db.session.commit()
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")


@admin.route('/define-subject', methods=['POST'])
def define_subject():
    if verif_admin():
        try:
            data = json.loads(request.data)
            codename = data['codename']
            define = data['define']
        except:
            return jsonify(result="Error: required subject's codename and defined value")
        subject = Subject.query.filter_by(codename=codename).first()
        if subject:
            subject.access = define
            db.session.commit()
            return jsonify(result="Success")
        return jsonify(result="Error: subject is not exist")
    else:
        return jsonify(result="Error: you aren't admin")