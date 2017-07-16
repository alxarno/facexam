from ..extensions import db
from config import SECRET_KEY
import json
import time
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    # pw_hash = db.Column(db.String(255))
    access = db.Column(db.SmallInteger, default=0)
    # subjects = [subject.codename, subject.codename, ...]
    subjects = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), nullable=False)
    tasks = db.relationship('Task', backref='author')
    statistic = db.relationship('AuthorStatistic', backref='author')
    static_tests = db.relationship('StaticTest', backref='author')

    def __init__(self, subjects=json.dumps([]), user_id=None):
        self.set_token(user_id)
        # self.set_password(password)
        self.subjects = subjects
        self.user_id = user_id

    def set_token(self, id):
        t = time.time()
        body = str(id).encode('utf8') + SECRET_KEY.encode('utf8')+str(t).encode('utf8')
        self.token = hashlib.sha1(body).hexdigest()


class AuthorStatistic(db.Model):
    __tablename__ = "authors_statistic"
    id = db.Column(db.Integer, primary_key=True)
    solve_tasks = db.Column(db.Integer(), default=0)
    time_reload = db.Column(db.Integer(), default=0)
    last_data = db.Column(db.String(), default='[]')
    author_id = db.Column(db.Integer(), db.ForeignKey('authors.id'))