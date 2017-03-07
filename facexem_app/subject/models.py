from ..extensions import db


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    themes = db.relationship('Theme', backref='subject')


class Theme(db.Model):
    __tablename__ = "subjects_themes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    lections = db.relationship('Lection', backref='theme')
    subject_id = db.Column(db.Integer(), db.ForeignKey('Subject.id'))


class Lection(db.Model):
    __tablename__ = "themes_lections"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    themes_id = db.Column(db.Integer(), db.ForeignKey('Theme.id'))