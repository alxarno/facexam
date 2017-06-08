from ..extensions import db
from .constans import ROLES
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from config import SECRET_KEY
import time
from ..achievements.models import Achievement


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(50), nullable=False)
    vk_id = db.Column(db.String(120), unique=True)
    google_id = db.Column(db.String(120), unique=True)
    token = db.Column(db.String(40),  default='')
    pw_hash = db.Column(db.String(70),  default='')
    profile_done = db.Column(db.SmallInteger, default=0)

    public_key = db.Column(db.String(32), default='')

    info_page = db.relationship('UserPage', backref='user')
    activity = db.relationship('UserActivity', backref='user')
    task_solve = db.relationship('TaskSolve', backref='user')
    test_solve = db.relationship('TestSolve', backref='user')
    sessions_task = db.relationship('SessionTasks', backref='user')
    subjects_statics = db.relationship('SubjectStatic', backref='user')

    reports = db.relationship('Issue', backref='user')

    def __init__(self, name=None, password=None, email=None, role=None, vk_id=None, google_id=None):
        self.name = name
        self.set_password(password)
        if vk_id:
            self.set_token(vk_id, SECRET_KEY)
            self.set_public_key(vk_id, SECRET_KEY)
            self.vk_id = vk_id
        if google_id:
            self.set_token(google_id, SECRET_KEY)
            self.set_public_key(google_id, SECRET_KEY)
            self.google_id = google_id
        if email:
            self.set_token(email, SECRET_KEY)
            self.set_public_key(email, SECRET_KEY)
            self.email = email
        self.role = role

    def set_public_key(self, smth_id, secret):
        t = time.time()
        self.public_key = hashlib.md5(smth_id.encode('utf8') + secret.encode('utf8')+str(t).encode('utf8')).hexdigest()

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_token(self, smth_id, secret):
        t = time.time()
        self.token = hashlib.sha1(smth_id.encode('utf8') + secret.encode('utf8')+str(t).encode('utf8')).hexdigest()

    def set_google_id(self, google_id):
        self.google_id = google_id

    def set_vk_id(self, vk_id):
        self.vk_id = vk_id

    def __repr__(self):
        return '<User %r>' % self.name


class TestUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    key = db.Column(db.String(20), unique=True)

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


class UserPage(db.Model):
    __tablename__ = "users_info_page"
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(64), nullable=False)
    about = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(64))
    experience = db.Column(db.Integer())
    lections = db.Column(db.Integer(), default=0)
    tasks = db.Column(db.Integer(), default=0)
    tests = db.Column(db.Integer(), default=0)
    last_actions = db.Column(db.String(512), default=u'')
    user_active_achivs = db.Column(db.String(256), default=u'')
    user_achievements = db.Column(db.String(1500), default=u'')
    user_active_background = db.Column(db.String(20), default=u'')
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

    def set_photo(self, photo):
        self.photo = photo

    def get_photo(self):
        return self.photo

    def set_about(self, about):
        self.about = about

    def set_active_achivs(self, achivs):
        self.user_active_achivs = achivs

    def __repr__(self):
        return '<UserPage %r>' % self.user_id



class SubjectStatic(db.Model):
    __tablename__ = "subjects_static"
    id = db.Column(db.Integer, primary_key=True)
    subject_codename = db.Column(db.String(30))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    date_reload = db.Column(db.Integer())
    test_points = db.Column(db.Integer())
    last_random_task_time = db.Column(db.Integer())
    best_session_list = db.Column(db.Integer())

    def __repr__(self):
        return '<SubjectStatic %r>' % self.id


class UserActivity(db.Model):
    __tablename__ = "user_activity"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    lections = db.Column(db.Integer, default=0)
    tasks = db.Column(db.Integer(), default=0)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

    def __repr__(self):
        return '<UserActivity %r>' % self.user_id



