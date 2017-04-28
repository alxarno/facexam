import json
from werkzeug.datastructures import ImmutableMultiDict
import os

from flask import Blueprint, request, jsonify
from config import UPLOAD_FOLDER

from .models import Achievement
from ..subject.models import Subject
from ..user.models import User
from ..user.constans import ROLES
from ..extensions import db
from werkzeug.utils import secure_filename

achievement = Blueprint('achievement', __name__, url_prefix='/api/achievement')


def verif_author(token=''):
    if token == '':
        try:
            data = json.loads(request.data)
            token = data['token']
        except:
            return False
    try:
        print(token)
        current_admin = User.query.filter_by(token=token).first()
        if current_admin:
            if (current_admin.role == ROLES['ADMIN']) or (current_admin.role == ROLES['AUTHOR']):
                return True
            else:
                return False
        else:
            return False
    except:
        return False


@achievement.route('/info', methods=['POST'])
def info_achievement():
    if verif_author():
        return jsonify(result="Success")
    else:
        return jsonify(result='Error')


@achievement.route('/get_all', methods=['POST'])
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


@achievement.route('/create', methods=['POST'])
def create():
    if verif_author():
        data = json.loads(request.data)
        try:
            name = data['name']
            content = data['content']
            type = data['type']
            max = data['max']
            condition = data['condition']
            subject_codename = data['subject_codename']
        except:
            return jsonify(result="Error")
        subject = Subject.query.filter_by(codename=subject_codename).first()
        if subject:
            new_achiev = Achievement(name=name, content=content, type=type, max=int(max),
                                     condition=json.dumps(condition), subject=subject)
            db.session.add(new_achiev)
            db.session.commit()
            return jsonify(result="Success")
        else:
            return jsonify(result="Error")
    else:
        return jsonify(result="Error")


@achievement.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    print(file)
    data = dict(request.form)
    if verif_author(data['token'][0]):
        try:
            name = data['name'][0]
            conent = data['content'][0]
            type = data['type'][0]
            condition = data["condition"][0]
        except:
            return jsonify(result="Error: not all data there are")

    # if file and file.filename:
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify(result="Success")


@achievement.route('/delete', methods=['POST'])
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
