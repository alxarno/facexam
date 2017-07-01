from flask import Blueprint, redirect, url_for, request, jsonify, session
import json,jwt, datetime
import time
from ..user.models import User, TestUser, UserPage,  UserActivity, SubjectStatic
from ..extensions import db
from ..subject.models import Subject, Task, Challenge, Content, Issue, TaskSolve
from .models import Author
from ..achievements.models import Achievement
from ..user.constans import ROLES
from config import ADMIN_KEY, AUTHOR_KEY, SECRET_KEY
import os, shutil
from config import SUBJECT_FOLDER, UPLOAD_FOLDER, TASK_FOLDER
from functools import wraps

author = Blueprint('author', __name__, url_prefix='/api/author')


def verification_author(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            data = json.loads(request.data)
            token = data['token']
            data_token = jwt.decode(token, SECRET_KEY)
            user_token = data_token['public']
            now_user = Author.query.filter_by(token=user_token).first()
            if now_user:
                return f(now_user, *args, **kwargs)
            else:
                return jsonify({"result": 'Error', "type": 'Author is required'})
        except:
            return jsonify({"result": 'Error', "type": 'Verification is fail'})
    return wrapper


def verif_author(token='', user_code=''):
    # try:
    #     data = json.loads(request.data)
    #     token = data['token']
        data_token = jwt.decode(token, SECRET_KEY)
        user_token = data_token['public']
        current_author = Author.query.filter_by(token=user_token).first()
        if current_author:
            if 'a_token' in session:
                if session['a_token'] == token:
                    return current_author
            else:
                if user_code == ADMIN_KEY:
                    return current_author
        else:
            return False
    # except:
    #     return False

    # else:
        # current_author =



@author.route('/login', methods=['POST'])
def login():
    if 'token' in session:
        token = session['token']
        data_token = jwt.decode(token, SECRET_KEY)
        user_token = data_token['public']
        user = User.query.filter_by(token=user_token).first()
        if user:
            author = Author.query.filter_by(user_id=user.id).first()
            if author:
                key = jwt.encode({'public': author.token, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=12000)},
                                 SECRET_KEY)
                session['a_token'] = key.decode('UTF-8')
                return jsonify(key.decode('UTF-8'))
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
@verification_author
def get_info(now_user):
    return jsonify(result='yes')


@author.route('/my_achievs', methods=['POST'])
@verification_author
def my_achievs(wr_user):
    achievs = Achievement.query.filter_by(author_id=wr_user.id)
    final = []
    for i in achievs:
        final.append({
            "name": i.name,
            "content": i.content,
            'id': i.id
        })
    return jsonify(final)


@author.route('/my_subjects', methods=['POST'])
@verification_author
def my_subjects(wr_user):
    final = []
    subjects = json.loads(wr_user.subjects)
    for i in subjects:
        subject = Subject.query.filter_by(codename=i).first()
        count = Task.query.filter_by(subject_id=subject.id).count()
        if subject:
            try:
                final.append({
                        "codename": subject.codename,
                        "name": subject.name,
                        "count": count,
                        "points": json.loads(subject.system_points),
                        "themes": json.loads(subject.additional_themes)
                    })
            except:
                None
    return jsonify(final)


@author.route('/get_achievement', methods=['POST'])
@verification_author
def get_achievement(wr_user):
    try:
        data = json.loads(request.data)
        id = data['id']
    except:
        return jsonify(result='Error')
    achiev = Achievement.query.filter_by(id=id).first()
    if wr_user.id == achiev.author_id:
        subject = Subject.query.filter_by(id=achiev.subject_id).first()
        return jsonify({"name": achiev.name, "content": achiev.content, "type": achiev.type,
                        "max": achiev.max, "condition": achiev.condition, "subject": subject.codename})
    return jsonify(result='Error')


@author.route('/save_yet_create_achieve', methods=['POST'])
@verification_author
def save_achievement(wr_user):
    try:
        data = json.loads(request.data)
        id = data['id']
    except:
        return jsonify(result='Error')
    achiev = Achievement.query.filter_by(id=id).first()
    if wr_user.id == achiev.author_id:
        subject = Subject.query.filter_by(id=achiev.subject_id).first()
        return jsonify({"name": achiev.name, "content": achiev.content, "type": achiev.type,
                        "max": achiev.max, "condition": achiev.condition, "subject": subject.codename})
    return jsonify(result='Error')


@author.route('/my_tasks', methods=['POST'])
@verification_author
def my_tasks(wr_user):
    tasks = Task.query.filter_by(author_id=wr_user.id).all()
    final = []
    subjects = {}
    for i in tasks:
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



@author.route('/create_task', methods=['POST'])
@verification_author
def create_task(wr_user):
    try:
        data = json.loads(request.data)
        number = data['number']
        codename = data['codename']
        themes = data['themes']
    except:
        return jsonify(result='Error')
    subject = Subject.query.filter_by(codename=codename).first()
    if subject:
        task = Task(number=number, open=0, subject_id=subject.id, author_id=wr_user.id, themes=json.dumps(themes))
        db.session.add(task)
        db.session.commit()
        content = Content(content=json.dumps([{'type': "mainquest", 'content': []}]), description=json.dumps([]),
                          answers=json.dumps([]), task_id=task.id)
        path = TASK_FOLDER
        path = path + '/' + str(task.id)
        if not os.path.exists(path):
            os.makedirs(path)
        db.session.add(content)
        db.session.commit()
        return jsonify(result='/task/redactor/' + str(task.id))
    return jsonify(result='Error')


@author.route('/task_images/<id>', methods=['POST'])
@verification_author
def task_images(wr_user, id):
    task = Task.query.filter_by(id=id).first()
    if task:
        path = TASK_FOLDER + '/' + id
        print(path)
        if os.path.exists(path):
            result = os.listdir(path)
            return jsonify(result)
        return jsonify({"result": 'Error', "type": 'Folder is undefined'})
    return jsonify({"result": 'Error', "type": 'Task is undefined'})


@author.route('/download_task_img/<id>', methods=['POST'])
def download_task_img(id):
    file = request.files['file']
    data = dict(request.form)
    author = verif_author(data['token'][0], data['code'][0])
    if author:
        task = Task.query.filter_by(id=id).first()
        if task and file:
            path = TASK_FOLDER + '/' + id
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
@verification_author
def delete_img(wr_user):
    try:
        data = json.loads(request.data)
        id = data['id']
        name = data['name']
    except:
        return jsonify(result='Error')
    task = Task.query.filter_by(id=id).first()
    if task:
        path = TASK_FOLDER + '/' + str(id) + '/' + str(name) + '.png'
        if os.path.exists(path):
            os.remove(path)
            return jsonify(result='Success')


@author.route('/save_task_content', methods=['POST'])
@verification_author
def save_task_content(wr_user):
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
    return jsonify({"result": 'Error', "type": 'Task is undefined'})


@author.route('/get_task_content', methods=['POST'])
@verification_author
def get_task_content(wr_user):
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
    return jsonify({"result": 'Error', "type": 'Task is undefined'})


@author.route('/delete_task', methods=['POST'])
@verification_author
def delete_task(wr_user):
    try:
        data = json.loads(request.data)
        id = data['id']
    except:
        return jsonify({"result": 'Error', "type": 'ID is required'})
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
        path = TASK_FOLDER + '/' + str(id)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=False, onerror=None)
        return jsonify(result='Success')
    return jsonify({"result": 'Error', "type": 'Task is undefined'})


@author.route('/query_task', methods=['POST'])
@verification_author
def query_task(wr_user):
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
        if i:
            subject = Subject.query.filter_by(id=i.subject_id).first()
            final.append({'id': i.id, 'number': i.number, 'open': i.open, 'subject': subject.codename})
    return jsonify(final)


@author.route('/get_my_issues', methods=['POST'])
@verification_author
def get_my_issues(wr_user):
    final = []
    query = Issue.query.filter_by(author_id=wr_user.id).all()
    for i in query:
        final.append({
            'content': i.content,
            'solve': i.solve,
            'task_id': i.task_id,
            'issue_id': i.id
        })
    return jsonify(final)


@author.route('/delete-issue', methods=['POST'])
@verification_author
def delete_issue(wr_user):
    try:
        data = json.loads(request.data)
        id = data['id']
    except:
        return jsonify({"result": 'Error', "type": 'Id is required'})
    query = db.session.query(Issue).filter_by(id=id).first()
    if query:
        db.session.delete(query)
        db.session.commit()
    return jsonify(result='Success')


@author.route('/set_availability', methods=['POST'])
@verification_author
def availability(wr_user):
    try:
        data = json.loads(request.data)
        id = data['id']
        value = data['value']
    except:
        return jsonify({"result": 'Error', "type": 'Id and Value are required'})
    task = Task.query.filter_by(id=id).first()
    task.open = value
    db.session.commit()
    return jsonify(result='Success')


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
@verification_author
def delete():
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


@author.route('/achiev/change', methods=['POST'])
def change():
    data = dict(request.form)
    if verif_author(data['token'][0], '232323'):
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
            return jsonify({"result": 'Error', "type": 'Achievement is undefine'})
    else:
        return jsonify({"result": 'Error', "type": 'Author is required'})


@author.route('/achiev/get_all', methods=['POST'])
@verification_author
def get_all():
    final = []
    achievs = Achievement.query.all()
    for i in achievs:
        final.append({'id': i.id, 'name': i.name, 'content': i.content, 'type': i.type,
                      'subject_id': i.subject_id, 'user_id': i.user_id})
    return jsonify(final)
