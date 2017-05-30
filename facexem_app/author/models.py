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
    pw_hash = db.Column(db.String(255))
    # subjects = [subject.codename, subject.codename, ...]
    subjects = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), nullable=False)
    tasks = db.relationship('Task', backref='author')

    def __init__(self, subjects=json.dumps([]), password=None, user_id=None):
        self.set_token(user_id)
        self.set_password(password)
        self.subjects = subjects
        self.user_id = user_id

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def set_token(self, id):
        t = time.time()
        body = str(id).encode('utf8') + SECRET_KEY.encode('utf8')+str(t).encode('utf8')
        self.token = hashlib.sha1(body).hexdigest()

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)