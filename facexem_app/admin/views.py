import json

from flask import Blueprint, request, jsonify

from ..user.models import User, TestUser
from ..user.constans import ROLES
from ..extensions import db

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


def verif_admin():
    data = json.loads(request.data)
    token = data['token']
    current_admin = User.query.filter_by(token=token).first()
    if current_admin:
        if current_admin.role == ROLES['ADMIN']:
            return True
        else:
            return False
    else:
        return False


@admin.route('/info', methods=['POST'])
def info_admin():
    if verif_admin():
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")


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


