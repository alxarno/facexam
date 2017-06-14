from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from config import SECRET_KEY
import time


class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(40))
    pw_hash = db.Column(db.String(70))
    email = db.Column(db.String(50))

    def __init__(self, name=None, password=None, email=None):
        self.name = name
        self.pw_hash = generate_password_hash(password)
        self.set_token(email)
        if email:
            self.email = email

    def set_token(self, email):
        t = time.time()
        body = email.encode('utf8') + SECRET_KEY.encode('utf8') + str(t).encode('utf8')
        self.token = hashlib.sha1(body).hexdigest()

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)