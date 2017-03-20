import json

from flask import Blueprint, request, jsonify

from .models import Achievement
from ..subject.models import Subject
from ..user.models import User
from ..user.constans import ROLES
from ..extensions import db

achievement = Blueprint('achievement', __name__, url_prefix='/api/achievement')


def verif_author():
    try:
        data = json.loads(request.data)
        token = data['token']
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
                          'subject_id': i.subject_id })
        return jsonify(final)
    else:
        return jsonify(result="Error")


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
