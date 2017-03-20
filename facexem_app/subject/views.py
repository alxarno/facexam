from flask import Blueprint, jsonify, request
from ..extensions import db
import json
from .models import Subject, Lection, Theme, Task
from ..user.models import User
from ..user.constans import ROLES

subject = Blueprint('subject', __name__, url_prefix='/api/subject')


def verif_author():
    try:
        data = json.loads(request.data)
        token = data['token']
        current_admin = User.query.filter_by(token=token).first()
        if current_admin:
            if (current_admin.role == ROLES['ADMIN']) or (current_admin.role == ROLES['AUTHOR']) :
                return True
            else:
                return False
        else:
            return False
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
        return jsonify(result='error')


@subject.route('/get_themes', methods=['POST'])
def get_themes():
    if verif_author():
        themes = Theme.query.all()
        result = []
        for theme in themes:
            subject_of_theme = Subject.query.get(theme.subject_id)
            result.append({'name': theme.name, 'subject': subject_of_theme.name, 'id': theme.id})
        return jsonify(result)
    else:
        return jsonify(result='error')


@subject.route('/get_lections', methods=['POST'])
def get_lections():
    if verif_author():
        try:
            data = json.loads(request.data)
            subject_code_name = data['subject_code_name']
        except:
            return jsonify(result='error')
        current_subject = Subject.query.filter_by(codename=subject_code_name).first()
        if current_subject:
            themes = current_subject.themes
            theme = []
            for j in themes:
                lections = j.lections
                lections_final = []
                for k in lections:
                    lections_final.append({"id": k.id, "name": k.name})
                theme.append({'name': j.name, 'lections': lections_final})
            return jsonify(theme)
        else:
            return jsonify(result='Error: this subject havent')


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


@subject.route('/create_theme', methods=['POST'])
def create_theme():
    if verif_author():
        try:
            data = json.loads(request.data)
            subject_code = data['subject_code']
            name = data['name']
        except:
            jsonify(result='Error')
        current_subject = Subject.query.filter_by(codename=subject_code).first()
        if current_subject:
            theme = Theme(name=name, subject=current_subject)
            db.session.add(theme)
            db.session.commit()
            print("Theme " + name + " is created")
            return jsonify(result='Success')
        else:
            return jsonify(result='Error: this subject havent')
    else:
        return jsonify(result='Error')


@subject.route('/create_lection', methods=['POST'])
def create_lection():
    if verif_author():
        try:
            data = json.loads(request.data)
            theme_id = data['theme_id']
            lection_name = data['lection_name']
            lection_description = data['description']
            lection_type = data['type']
            lection_content = json.dumps(data['lection_content'])
        except:
            return jsonify(result='Error')
        current_them = Theme.query.get(theme_id)
        if current_them:
            l = Lection(name=lection_name, content=lection_content, theme=current_them,
                        description=lection_description, type=lection_type)
            db.session.add(l)
            db.session.commit()
            return jsonify(result='Success')
        else:
            return jsonify(result='Error: this theme havent')
    else:
        return jsonify(result='Error')


@subject.route('/delete_lection', methods=['POST'])
def delete_lection():
    if verif_author():
        try:
            data = json.loads(request.data)
            lection_id = data['id']
        except:
            return jsonify(result='Error')
        u = Lection.query.filter_by(id=lection_id).first()
        if u:
            u.delete()
            db.session.commit()
            return jsonify(result='Success')
        else:
            return jsonify(result='Error: this lection havent')
    else:
        return jsonify(result='Error')


@subject.route('/get_tasks', methods=['POST'])
def get_tasks():
    if verif_author():
        try:
            data = json.loads(request.data)
            subject_code_name = data['subject_code_name']
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
            subject_codename = data['subject_code_name']
            task_number = data['task_number']
            content = data['content']
            answer = data['answer']
            description = data['description']
        except:
            return jsonify(result='Error')
        current_subject = Subject.query.filter_by(codename=subject_codename).first()
        if current_subject:
            task = Task(number=task_number, content=json.dumps(content), answer=answer,\
                        description=json.dumps(description), subject=current_subject)
            db.session.add(task)
            db.session.commit()
            return jsonify(result="Success")
        else:
            return jsonify(result="Error")
    else:
        return jsonify(result='Error')
