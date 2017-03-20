from ..extensions import db


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    access = db.Column(db.Integer())
    codename = db.Column(db.String(64))
    themes = db.relationship('Theme', backref='subject')
    tasks = db.relationship('Task', backref='subject')
    achievements = db.relationship('Achievement', backref='subject')


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

