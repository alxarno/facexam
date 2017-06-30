import json
import time
import datetime
import random
import os


from flask import Blueprint, request, jsonify, session

from ..user.models import User, TestUser,  UserPage
from ..user.constans import ROLES
from ..subject.models import Task, Subject, Challenge, TaskSolve
from ..extensions import db
from .models import Admin
from config import ADMIN_KEY, AUTHOR_KEY, SUBJECT_FOLDER
from ..author.models import Author
from ..achievements.models import Achievement

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


def verif_admin(data =''):
    if data == '':
        data = json.loads(request.data)
    try:
        token = data['token']
        code = data['code']
        current_admin = Admin.query.filter_by(token=token).first()
        if current_admin:
                if 'token' in session:
                    if session['token'] == token:
                        return current_admin
                elif code == ADMIN_KEY:
                    return current_admin
    except:
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


# @admin.route('/smth', methods=['POST'])
# def smth():
#     if verif_admin():
#         data = json.loads(request.data)
#         token = data['token']
#         subject = data['subject']
#         now_time = time.localtime()
#         now_date = datetime.date(now_time.tm_year, now_time.tm_mon, now_time.tm_mday)
#         # creating array with last 7 days dates
#         dates = []
#         final = {}
#         i = 6
#         while i >= 0:
#             date = now_date - datetime.timedelta(days=i)
#             dates.append(str(date))
#             i -= 1
#         for i in dates:
#             final[i] = random.randint(0, 100)
#         current_admin = User.query.filter_by(token=token).first()
#         real_subjects = current_admin.info_subjects
#         r_subject = 0
#         for j in real_subjects:
#             if j.subject_codename == subject:
#                 r_subject = j
#         sub = UserSubjects.query.filter_by(id=r_subject.id).first()
#         sub.activity = json.dumps(final)
#         db.session.commit()
#         return jsonify(result="Success")
#     else:
#         return jsonify(result="Error")


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


@admin.route('/create-author', methods=['POST'])
def create_author():
    admin = verif_admin()
    if admin:
        try:
            data = json.loads(request.data)
            yid = data['key']
            subjects = data['subjects']
            current_user = User.query.filter_by(public_key=yid).first()
            if current_user:
                current_author = Author.query.filter_by(user_id=current_user.id).first()
                if current_author is None:
                    a = Author(subjects=json.dumps(subjects), user_id=current_user.id)
                    db.session.add(a)
                    db.session.commit()
                    return jsonify(result='Success')
        except:
            None
    return jsonify(resultl='Error')


@admin.route('/create-subject', methods=['POST'])
def create_subject():
    data = dict(request.form)
    data = json.loads(data['data'][0])
    admin = verif_admin(data)
    if admin:
        file = request.files['file']
        subject = Subject(name=data['name'], system_points=json.dumps(data['points']),
                          access=0, codename=data['codename'], time_pass=int(data['time_limit'])*60,
                          min_point_test=int(data['min_point']), additional_themes=json.dumps(data['addThemes']))
        db.session.add(subject)
        db.session.commit()
        if file and file.filename:
            file.save(os.path.join(SUBJECT_FOLDER, str(data['codename']) + '.png'))
        return jsonify(result='Success')
    return jsonify(result='Error')


@admin.route('/get_subjects', methods=['POST'])
def my_subjects():
    admin = verif_admin()
    if admin:
        final = []
        subjects = Subject.query.all()
        for i in subjects:
            count = Task.query.filter_by(subject_id=i.id).count()
            final.append({
                    "codename": i.codename,
                    "name": i.name,
                    "count": count,
                    "open": i.access
                })
        return jsonify(final)
    else:
        return jsonify(result='Error')


@admin.route('/get_subject_info', methods=['POST'])
def get_subject_info():
    admin = verif_admin()
    if admin:
        try:
            data = json.loads(request.data)
            codename = data['codename']
            subject = Subject.query.filter_by(codename=codename).first()
            if subject:
                tasks = Task.query.filter_by(subject_id=subject.id).count()
                achievs = Achievement.query.filter_by(subject_id=subject.id).count()
                challenges = Challenge.query.filter_by(subject_id=subject.id).count()
                add_themes = []
                try:
                    add_themes = json.loads(subject.additional_themes)
                except:
                    None
                final = {
                    "name": subject.name,
                    "time": subject.time_pass/60,
                    "min_point": subject.min_point_test,
                    "points": json.loads(subject.system_points),
                    "add_themes": add_themes,
                    "access": subject.access,
                    "codename": subject.codename,
                    "task": tasks,
                    "achievs": achievs,
                    "chall": challenges
                }
                return jsonify(final)
        except:
            return jsonify(result="Error")
    return jsonify(result="Error")


@admin.route('/save_subject_info', methods=['POST'])
def save_subject_info():
    data = dict(request.form)
    data = json.loads(data['data'][0])
    admin = verif_admin(data)
    if admin:
        # try:
            name = data['name']
            access = data['access']
            codename = data['codename']
            points = data['points']
            time_pass = data['time']
            min_point = data['min_point']
            add_themes = data['add_themes']
            subject = Subject.query.filter_by(codename=codename).first()
            if subject:
                subject.name = name
                subject.access = access
                subject.time_pass = int(time_pass)*60
                subject.min_point_test = min_point
                subject.system_points = json.dumps(points)
                subject.additional_themes = json.dumps(add_themes)
                db.session.commit()
                if data['file']:
                    file = request.files['file']
                    if file and file.filename:
                        file.save(os.path.join(SUBJECT_FOLDER, str(data['codename']) + '.png'))
                return jsonify(result='Success')
        # except:
        #     return jsonify(result='Error')
    else:
        return jsonify(result='Error')


@admin.route('/get_all_authors', methods=['POST'])
def get_all_authors():
    admin = verif_admin()
    if admin:
        authors = Author.query.all()
        final = []
        user_id = []
        for i in authors:
            user_id.append(i.user_id)
            final.append({
                "tasks": len(i.tasks),
                "access": i.access
            })
        all = db.session.query(User, UserPage).join(UserPage).filter(User.id.in_(user_id)).all()
        for i in range(len(authors)):
            final[i]['name'] = all[i].User.name
            final[i]['photo'] = all[i].UserPage.photo+'.png'
            final[i]['id'] = all[i].User.id
        return jsonify(final)
    return jsonify(resilt='Error')


@admin.route('/get_author_info', methods=['POST'])
def get_author_info():
    admin = verif_admin()
    if admin:
        try:
            data = json.loads(request.data)
            id = data['id']
            user = User.query.filter_by(id=id).first()
            if user:
                user_page = UserPage.query.filter_by(user_id=user.id).first()
                author = Author.query.filter_by(user_id=user.id).first()
                final = {
                    "name": user.name,
                    'email': user.email,
                    'vk': user.vk_id,
                    'key': user.public_key,
                    'access': author.access,
                    'subjects': json.loads(author.subjects),
                    'city': user_page.city
                }
                return jsonify(final)
        except:
            return jsonify(result='Error')
    return jsonify(result='Error')


@admin.route('/set_author_info', methods=['POST'])
def set_author_info():
    admin = verif_admin()
    if admin:
        try:
            data = json.loads(request.data)
            id = data['id']
            data = data['data']
            access = data['access']
            subjects = data['subjects']
            author = Author.query.filter_by(user_id=id).first()
            if author:
                author.access = access
                author.subjects = json.dumps(subjects)
                db.session.commit()
                return jsonify(request='Success')
        except:
            return jsonify(result='Error')
    return jsonify(result='Error')


@admin.route('/delete_task_solve', methods=['POST'])
def delete_task():
    admin = verif_admin()
    if admin:
        TaskSolve.query.delete()
        db.session.commit()
    return jsonify(result='Hello')

