from ..extensions import db
from .constans import ROLES
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from config import SECRET_KEY
import base64
import time



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(64), nullable=False)
    vk_id = db.Column(db.String(120), unique=True)
    google_id = db.Column(db.String(120), unique=True)
    token = db.Column(db.String(255))
    pw_hash = db.Column(db.String(255))
    role = db.Column(db.SmallInteger, default=ROLES['USER'])

    def __init__(self, name=None, password=None, email=None, role=None, vk_id=None, google_id=None):
        self.name = name
        if password:
            self.set_password(password)
        if vk_id:
            self.set_token(vk_id, SECRET_KEY)
            self.vk_id = vk_id
        if google_id:
            self.set_token(google_id, SECRET_KEY)
            self.google_id = google_id
        if email:
            self.set_token(email, SECRET_KEY)
            self.email = email
        self.role = role

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_token(self, smth_id, secret):
        self.token = hashlib.sha1(smth_id.encode('utf8') + secret.encode('utf8')).hexdigest()

    def set_google_id(self, google_id):
        self.google_id = google_id

    def set_vk_id(self, vk_id):
        self.vk_id = vk_id

    def get_token(self):
        return self.token

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' % self.name


class TestUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    key = db.Column(db.String(20),  unique=True)

    def __init__(self, email=None):
        self.email = email
        self.get_key(email)

    def get_key(self, email):
        now_time = str(time.time())
        string = email + now_time
        h = hashlib.new('ripemd160')
        h.update(string.encode('utf8'))
        encoded = h.hexdigest()
        self.key = encoded[0::3]

    def __repr__(self):
        return '<TestUser %r>' % self.key
