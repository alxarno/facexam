from flask import Blueprint, jsonify, request
from ..extensions import db
import json
from .models import Subject, Lection, Theme

subject = Blueprint('subject', __name__, url_prefix='/subject')


@subject.route('/get_info', methods=['POST'])
def get_info():
    return jsonify(result='yes')


@subject.route('/get_subjects', methods=['POST'])
def get_subjects():
    subjects = Subject.query.all()
    result = []
    for sub in subjects:
        result.append({'name': sub.name, 'codename': sub.codename})
    return jsonify(result)


@subject.route('/get_themes', methods=['POST'])
def get_themes():
    themes = Theme.query.all()
    result = []
    for theme in themes:
        subject_of_theme = Subject.query.get(theme.subject_id)
        result.append({'name': theme.name, 'subject': subject_of_theme.name, 'id': theme.id})
    return jsonify(result)


@subject.route('/get_lections', methods=['POST'])
def get_lections():
    data = json.loads(request.data)
    subject_code_name = data['subject_code_name']
    current_subject = Subject.query.filter_by(codename=subject_code_name).first()
    if current_subject:
        themes = current_subject.themes
        theme = []
        for j in themes:
            lections = j.lections
            lections_final = []
            for k in lections:
                lections_final.append(json.loads(k.content))
            theme.append({'name': j.name, 'lections': lections_final})
        return jsonify(theme)
    else:
        return jsonify(result='Error: this subject havent')


@subject.route('/create_subject', methods=['POST'])
def create_subject():
    data = json.loads(request.data)
    name = data['name']
    codename = data['codename']
    current_subject = Subject.query.filter_by(codename=codename).first()
    if current_subject is None:
        s = Subject(name=name, access=0, codename=codename)
        db.session.add(s)
        db.session.commit()
        return jsonify(result='Success')
    else:
        return jsonify(result='Error: codename is already exist')


@subject.route('/create_theme', methods=['POST'])
def create_theme():
    data = json.loads(request.data)
    subject_code = data['subject_code']
    name = data['name']
    current_subject = Subject.query.filter_by(codename=subject_code).first()
    if current_subject:
        theme = Theme(name=name, subject=current_subject)
        db.session.add(theme)
        db.session.commit()
        print("Theme " + name + " is created")
        return jsonify(result='Success')
    else:
        return jsonify(result='Error: this subject havent')


@subject.route('/create_lection', methods=['POST'])
def create_lection():
    data = json.loads(request.data)
    theme_id = data['theme_id']
    lection_name = data['lection_name']
    lection_content = json.dumps(data['lection_content'])
    current_them = Theme.query.get(theme_id)
    if current_them:
        l = Lection(name=lection_name, content=lection_content, theme=current_them)
        db.session.add(l)
        db.session.commit()
        return jsonify(result='Success')
    else:
        return jsonify(result='Error: this theme havent')
