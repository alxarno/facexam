from flask import Blueprint, redirect, url_for, request, jsonify, session
import json
from ..user.models import User, TestUser, UserPage, UserSubjects, UserActivity
from ..extensions import db
from ..subject.models import Subject, Task, Challenge
from ..achievements.models import Achievement
from ..user.constans import ROLES
from config import ADMIN_KEY, AUTHOR_KEY

author = Blueprint('author', __name__, url_prefix='/api/author')


def verif_author():
    try:
        data = json.loads(request.data)
        token = data['token']
        current_author = User.query.filter_by(token=token).first()
        if current_author:
            if (current_author.role == ROLES['ADMIN']) or (current_author.role == ROLES['AUTHOR']):
                if 'token' in session:
                    if session['token'] == token:
                        return current_author
                    else:
                        return False
                else:
                    try:
                        user_code = data['code']
                    except:
                        return False
                    if (user_code == ADMIN_KEY) or (user_code == AUTHOR_KEY):
                        return current_author
                    else:
                        return False
            else:
                return False
        else:
            return False
    except:
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



