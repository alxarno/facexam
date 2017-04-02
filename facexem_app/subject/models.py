from ..extensions import db


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    system_points = db.Column(db.String(256))
    access = db.Column(db.Integer())
    codename = db.Column(db.String(64))
    themes = db.relationship('Theme', backref='subject')
    tasks = db.relationship('Task', backref='subject')
    achievements = db.relationship('Achievement', backref='subject')
    challenges = db.relationship('Challenge', backref='subject')


class Theme(db.Model):
    __tablename__ = "subjects_themes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    lections = db.relationship('Lection', backref='theme')
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))


class Lection(db.Model):
    __tablename__ = "themes_lections"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    type = db.Column(db.String(20))
    content = db.Column(db.String(10000))
    themes_id = db.Column(db.Integer(), db.ForeignKey('subjects_themes.id'))


class Task(db.Model):
    __tablename__ = "subjects_tasks"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer())
    content = db.Column(db.String(1000))
    answer = db.Column(db.String(64))
    description = db.Column(db.String(2000))
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))


class Challenge(db.Model):
    __tablename__ = "challenges"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(128))
    type = db.Column(db.String(10))
    max = db.Column(db.Integer())
    prize = db.Column(db.Integer())
    condition = db.Column(db.String(20))
    level_hard = db.Column(db.Integer())
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))