from ..extensions import db


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    system_points = db.Column(db.String(256))
    access = db.Column(db.Integer())
    codename = db.Column(db.String(64))
    tasks = db.relationship('Task', backref='subject')
    achievements = db.relationship('Achievement', backref='subject')
    challenges = db.relationship('Challenge', backref='subject')


class Task(db.Model):
    __tablename__ = "subjects_tasks"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer())
    open = db.Column(db.Integer())
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    content = db.relationship('Content', backref='task')


class Content(db.Model):
    __tablename__ = "tasks_content"
    id = db.Column(db.Integer, primary_key=True)
    mainquest = db.Column(db.String(1000))
    quests = db.Column(db.String(1000))
    answers = db.Column(db.String(1000))
    task_id = db.Column(db.Integer(), db.ForeignKey('subjects_tasks.id'))


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