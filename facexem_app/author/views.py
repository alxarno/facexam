from flask import Blueprint, redirect, url_for, request, jsonify, session
import json
import time
from ..user.models import User, TestUser, UserPage, UserSubjects, UserActivity
from ..extensions import db
from ..subject.models import Subject, Task, Challenge, Content
from ..achievements.models import Achievement
from ..user.constans import ROLES
from config import ADMIN_KEY, AUTHOR_KEY
import os, shutil
from config import SUBJECT_FOLDER

author = Blueprint('author', __name__, url_prefix='/api/author')


def verif_author(token='', user_code=''):
    try:
        data = json.loads(request.data)
        token = data['token']
        user_code = data['code']
    except:
        data = ''
    current_author = User.query.filter_by(token=token).first()
    if current_author:
        if (current_author.role == ROLES['ADMIN']) or (current_author.role == ROLES['AUTHOR']):
            if 'token' in session:
                if session['token'] == token:
                    return current_author
                else:
                    return False
            else:
                if (user_code == ADMIN_KEY) or (user_code == AUTHOR_KEY):
                    return current_author
                else:
                    return False
        else:
            return False
    else:
        return False


@author.route('/get_info', methods=['POST'])
def get_info():
    author = verif_author()
    if author:
        return jsonify(result='yes')
    else:
        return jsonify(result='error')


@author.route('/my_achievs', methods=['POST'])
def my_achievs():
    author = verif_author()
    if author:
        achievs = Achievement.query.filter_by(user=author)
        final = []
        for i in achievs:
            final.append({
                "name": i.name,
                "content": i.content,
                'id': i.id
            })
        return jsonify(final)
    else:
        return jsonify(result='Error')


@author.route('/my_subjects', methods=['POST'])
def my_subjects():
    author = verif_author()
    if author:
        final = []
        subjects = Subject.query.all()
        for i in subjects:
            final.append({
                "codename": i.codename,
                "name": i.name
            })
        return jsonify(final)
    else:
        return jsonify(result='Error')


@author.route('/get_achievement', methods=['POST'])
def get_achievement():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
        except:
            return jsonify(result='Error')
        achiev = Achievement.query.filter_by(id=id).first()
        if author.id == achiev.author_id:
            subject = Subject.query.filter_by(id=achiev.subject_id).first()
            return jsonify({"name": achiev.name, "content": achiev.content, "type": achiev.type,
                            "max": achiev.max, "condition": achiev.condition, "subject": subject.codename})
        return jsonify(result='Error')
    else:
        return jsonify(result='Error')


@author.route('/save_yet_create_achieve', methods=['POST'])
def save_achievement():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
        except:
            return jsonify(result='Error')
        achiev = Achievement.query.filter_by(id=id).first()
        if author.id == achiev.author_id:
            subject = Subject.query.filter_by(id=achiev.subject_id).first()
            return jsonify({"name": achiev.name, "content": achiev.content, "type": achiev.type,
                            "max": achiev.max, "condition": achiev.condition, "subject": subject.codename})
        return jsonify(result='Error')
    else:
        return jsonify(result='Error')


@author.route('/my_tasks', methods=['POST'])
def my_tasks():
    author = verif_author()
    if author:
        achiev = Task.query.filter_by(author_id=author.id)
        final = []
        subjects = {}
        for i in achiev:
            if i.subject_id in subjects:
                subject = subjects[i.subject_id]
            else:
                subject = Subject.query.filter_by(id=i.subject_id).first()
                if subject:
                    subject = subject.name
                    subjects[i.subject_id] = subject
                else:
                    subject = 'Error'
            final.append({"id": i.id, "number": i.number, "subject": subject, "open": i.open})
        return jsonify(final)
    else:
        return jsonify(result='Error')


@author.route('/create_task', methods=['POST'])
def create_task():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            number = data['number']
            codename = data['codename']
        except:
            return jsonify(result='Error')
        subject = Subject.query.filter_by(codename=codename).first()
        if subject:
            task = Task(number=number, open=0, subject_id=subject.id, author_id=author.id)
            db.session.add(task)
            db.session.commit()
            content = Content(content=json.dumps([{'type': "mainquest", 'content': []}]), description=json.dumps([]),
                              answers=json.dumps([]), task_id=task.id)
            path = SUBJECT_FOLDER
            path = path + '/' + str(task.id)
            if not os.path.exists(path):
                os.makedirs(path)
            db.session.add(content)
            db.session.commit()
            return jsonify(result='/task/redactor/' + str(task.id))
        else:
            return jsonify(result='Error')
    else:
        return jsonify(result='Error')


@author.route('/task_images/<id>', methods=['POST'])
def task_images(id):
    author = verif_author()
    if author:
        task = Task.query.filter_by(id=id).first()
        if task:
            subject = Subject.query.filter_by(id=task.subject_id).first()
            if subject:
                path = SUBJECT_FOLDER + '/' + id
                if os.path.exists(path):
                    result = os.listdir(path)
                    return jsonify(result)
    return jsonify(result='Error')


@author.route('/download_task_img/<id>', methods=['POST'])
def download_task_img(id):
    file = request.files['file']
    data = dict(request.form)
    author = verif_author(data['token'][0], data['code'][0])
    if author:
        task = Task.query.filter_by(id=id).first()
        if task and file:
            path = SUBJECT_FOLDER + '/' + id
            if os.path.exists(path):
                name = []
                for i in str(time.time()):
                    if i != '.': name.append(i)
                name = ''.join(name)
                file.save(os.path.join(path, name + '.png'))
                return jsonify(name)
            else:
                os.makedirs(path)
                name = []
                for i in str(time.time()):
                    if i != '.': name.append(i)
                name = ''.join(name)
                file.save(os.path.join(path, name + '.png'))
                return jsonify(name)
    return jsonify(result='Error')


@author.route('/delete_img', methods=['POST'])
def delete_img():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
            name = data['name']
        except:
            return jsonify(result='Error')
        task = Task.query.filter_by(id=id).first()
        if task:
            path = SUBJECT_FOLDER + '/' + str(id) + '/' + str(name) + '.png'
            if os.path.exists(path):
                os.remove(path)
                return jsonify(result='Success')
    return jsonify(result='Error')


@author.route('/save_task_content', methods=['POST'])
def save_task_contetn():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
            content = data['data']
        except:
            return jsonify(result='Error')
        if Task.query.filter_by(id=id).first():
            content_task = Content.query.filter_by(task_id=id).first()
            content_task.content = json.dumps(content['content'])
            content_task.description = json.dumps(content['description'])
            content_task.answers = json.dumps(content['answers'])
            db.session.commit()
            return jsonify(result='Success')
    return jsonify(result='Error')


@author.route('/get_task_content', methods=['POST'])
def get_task_content():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
        except:
            return jsonify(result='Error')
        if Task.query.filter_by(id=id).first():
            content_task = Content.query.filter_by(task_id=id).first()
            answer = {'content': content_task.content,
                      'description': content_task.description,
                      'answers': content_task.answers}
            return jsonify(answer)
    return jsonify(result='Error')


@author.route('/delete_task', methods=['POST'])
def delete_task():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
        except:
            return jsonify(result='Error: data uncomplete')
        task = Task.query.filter_by(id=id).first()
        if task:
            task_content = Content.query.filter_by(task_id=id).first()
            if task_content:
                db.session.delete(task_content)
            db.session.delete(task)
            db.session.commit()
#         Delete files of task
            path = SUBJECT_FOLDER + '/' + str(id)
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=False, onerror=None)
            return jsonify(result='Success')
    return jsonify(result='Error')


@author.route('/query_task', methods=['POST'])
def query_task():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
            number = data['number']
            subject = data['subject']
        except:
            return jsonify(result='Error: data uncomplete')
        tasks = []
        final=[]
        if id != '':
            tasks.append(Task.query.filter_by(id=id).first())
        elif (number != '') and (subject != ''):
            subject = Subject.query.filter_by(codename=subject).first()
            tasks = Task.query.filter_by(number=number, subject_id=subject.id)
        elif number != '':
            tasks = Task.query.filter_by(number=number)
        elif subject != '':
            subject = Subject.query.filter_by(codename=subject).first()
            tasks = Task.query.filter_by(subject_id=subject.id)
            final = []
        for i in tasks:
            if i :
                subject = Subject.query.filter_by(id=i.subject_id).first()
                final.append({'id': i.id, 'number': i.number, 'open': i.open, 'subject': subject.codename})
        return jsonify(final)

    return jsonify(result='Error')


