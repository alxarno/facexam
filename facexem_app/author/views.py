from flask import Blueprint, redirect, url_for, request, jsonify, session
import json
import time
from ..user.models import User, TestUser, UserPage,  UserActivity, SubjectStatic
from ..extensions import db
from ..subject.models import Subject, Task, Challenge, Content, Issue, TaskSolve
from .models import Author
from ..achievements.models import Achievement
from ..user.constans import ROLES
from config import ADMIN_KEY, AUTHOR_KEY
import os, shutil
from config import SUBJECT_FOLDER, UPLOAD_FOLDER

author = Blueprint('author', __name__, url_prefix='/api/author')


def verif_author(token='', user_code=''):
    try:
        data = json.loads(request.data)
        token = data['token']
    except:
        data = {'code': user_code}
    current_author = Author.query.filter_by(token=token).first()
    if current_author:
        if 'a_token' in session:
            if session['a_token'] == token:
                return current_author
        else:
            code = data['code']
            if code == ADMIN_KEY:
                return current_author
    # else:
        # current_author =
    else:
        return False


@author.route('/login', methods=['POST'])
def login():
    if 'token' in session:
        token = session['token']
        user = User.query.filter_by(token=token).first()
        if user:
            author = Author.query.filter_by(user_id=user.id).first()
            if author:
                session['a_token'] = author.token
                return jsonify(author.token)
    # try:
    #     data = json.loads(request.data)
    #     code = data['code']
    #     u_token = data['u_token']
    # except:
    #     return jsonify(result='Error')
    # user = User.query.filter_by(token=u_token).first()
    # if user:
    #     author = Author.query.filter_by(user_id=user.id).first()
    #     if author:
    #         if code == AUTHOR_KEY:
    #             session['session_author'] = author.token
    #             return jsonify(author.token)
    return jsonify(result='Error')


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
        achievs = Achievement.query.filter_by(author_id=author.id)
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
        subjects = json.loads(author.subjects)
        for i in subjects:
            subject = Subject.query.filter_by(codename=i).first()
            count = Task.query.filter_by(subject_id=subject.id).count()
            if subject:
                final.append({
                        "codename": subject.codename,
                        "name": subject.name,
                        "count": count,
                        "points": json.loads(subject.system_points)
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
            subject = Subject.query.filter_by(id=task.subject_id).first()
            task_content = Content.query.filter_by(task_id=id).first()
            if task_content:
                db.session.delete(task_content)
            query = db.session.query(User, TaskSolve, SubjectStatic).filter(TaskSolve.task_id == task.id)
            query = query.join(SubjectStatic, SubjectStatic.subject_codename == subject.codename)
            for u, ts, st in query:
                if ts.solve == 1:
                    st.solve_delete_tasks += 1
                else:
                    st.unsolve_delete_tasks += 1
                db.session.commit()
                db.session.delete(ts)
                db.session.commit()
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


@author.route('/get_my_issues', methods=['POST'])
def get_my_issues():
    author = verif_author()
    if author:
        final = []
        query = db.session.query(Issue, Task).filter(Task.author_id == author.id)
        for i, t in query:
            final.append({
                'content': i.content,
                'solve': i.solve,
                'task_id': t.id,
                'issue_id': i.id
            })
        return jsonify(final)
    return jsonify(result='Error')


@author.route('/delete-issue', methods=['POST'])
def delete_issue():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
            query = db.session.query(Issue).filter_by(id=id).first()
            if query:
                db.session.delete(query)
                db.session.commit()
            return jsonify(result='Success')
        except:
            None
    return jsonify(result='Error')



@author.route('/set_availability', methods=['POST'])
def availability():
    author = verif_author()
    if author:
        try:
            data = json.loads(request.data)
            id = data['id']
            value = data['value']
        except:
            return jsonify(result='Error')
        task = Task.query.filter_by(id=id).first()
        task.open = value
        db.session.commit()
        return jsonify(result='Success')
    return jsonify(result='Error')


@author.route('/achiev/create', methods=['POST'])
def achiev_create():
    file = request.files['file']
    data = dict(request.form)
    data = json.loads(data['data'][0])
    author = verif_author(data['token'], "232323")
    if author:
        try:
            name = data['name']
            content = data['content']
            type = data['type']
            count = data['count']
            condition = data["add"]
            codename = data['subject']
        except:
            return jsonify(result="Error: not all data there are")
        subject = Subject.query.filter_by(codename=codename).first()
        if subject:
            new_achiev = Achievement(name=name, content=content, type=type, max=int(count),
                                     condition=json.dumps(condition), subject_id=subject.id, author_id=author.id)
            db.session.add(new_achiev)
            db.session.commit()
            if file and file.filename:
                file.save(os.path.join(UPLOAD_FOLDER, str(new_achiev.id)+'.png'))
            return jsonify(result="Success")
    return jsonify(result="Error")


@author.route('/achiev/delete', methods=['POST'])
def delete():
    if verif_author():
        data = json.loads(request.data)
        try:
            achievement_id = data['id']
        except:
            return jsonify(result="Error")
        achiev = Achievement.query.filter_by(id=achievement_id)
        if achiev.first():
            achiev.delete()
            db.session.commit()
            return jsonify(result='Success')
        else:
            return jsonify(result='Error')
    else:
        return jsonify(result="Error")


@author.route('/achiev/change', methods=['POST'])
def change():
    data = dict(request.form)
    if verif_author(data['token'][0]):
        try:
            name = data['name'][0]
            content = data['content'][0]
            count = data['count'][0]
            id = data['id'][0]
        except:
            return jsonify(result="Error: not all data there are")
        achiev = Achievement.query.filter_by(id=id).first()
        if achiev:
            achiev.name = name
            achiev.content = content
            achiev.count = count
            try:
                file = request.files['file']
                if file and file.filename:
                    file.save(os.path.join(UPLOAD_FOLDER, str(achiev.id)+'.png'))
                db.session.commit()
                return jsonify(result="Success")
            except:
                db.session.commit()
                return jsonify(result="Success")
        else:
            return jsonify(result="Error")
    else:
        return jsonify(result="Error")


@author.route('/achiev/get_all', methods=['POST'])
def get_all():
    if verif_author():
        final =[]
        achievs = Achievement.query.all()
        for i in achievs:
            final.append({'id': i.id, 'name': i.name, 'content': i.content, 'type': i.type,
                          'subject_id': i.subject_id, 'user_id': i.user_id})
        return jsonify(final)
    else:
        return jsonify(result="Error: you're not author")
