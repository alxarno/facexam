from ..extensions import db


class Achievement(db.Model):
    __tablename__ = "achievements"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    content = db.Column(db.String(256), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    max = db.Column(db.Integer(), nullable=False)
    condition = db.Column(db.String(20))
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

