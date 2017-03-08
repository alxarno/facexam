from ..extensions import db


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    access = db.Column(db.Integer())
    codename = db.Column(db.String(64))
    themes = db.relationship('Theme', backref='subject')


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
    content = db.Column(db.String(10000))
    themes_id = db.Column(db.Integer(), db.ForeignKey('subjects_themes.id'))
