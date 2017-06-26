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
    sessions = db.relationship('SessionTasks', backref='subject')
    time_pass = db.Column(db.Integer())
    min_point_test = db.Column(db.Integer())


class Task(db.Model):
    __tablename__ = "subjects_tasks"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer())
    open = db.Column(db.Integer())
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))
    author_id = db.Column(db.Integer(), db.ForeignKey('authors.id'))
    content = db.relationship('Content', backref='task')
    issues = db.relationship('Issue', backref='issue')
    solve_task = db.relationship('TaskSolve', backref='task')
    test_tasks = db.relationship('TestTask', backref='task')


class Content(db.Model):
    __tablename__ = "tasks_content"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(3000))
    description = db.Column(db.String(1000))
    answers = db.Column(db.String(500))
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


class Issue(db.Model):
    __tablename__ = "issues"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(128))
    solve = db.Column(db.Integer())
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer(), db.ForeignKey('subjects_tasks.id'))


class TaskSolve(db.Model):
    __tablename__ = 'task_solve'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer())
    count = db.Column(db.Integer())
    solve = db.Column(db.Integer())
    # type : 1=single, 2=random, 3=test
    type = db.Column(db.Integer())
    session_id = db.Column(db.Integer(), db.ForeignKey('session_tasks.id'))
    # date = db.Column(db.DateTime(timezone=False))
    alltime = db.Column(db.Integer())
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer(), db.ForeignKey('subjects_tasks.id'))
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }


class SessionTasks(db.Model):
    __tablename__ = 'session_tasks'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer())
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))
    key = db.Column(db.String(50))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    task_solve_id = db.relationship('TaskSolve', backref='task_solve')


class TestSolve(db.Model):
    __tablename__ = 'test_solve'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer())
    count = db.Column(db.Integer())
    need_count = db.Column(db.Integer())
    # type : 1=default, 2=personal
    type = db.Column(db.Integer())
    solve = db.Column(db.Integer())
    hundred_value = db.Column(db.Integer())
    hundred_need_count = db.Column(db.Integer())
    subject_id = db.Column(db.Integer(), db.ForeignKey('subjects.id'))
    alltime = db.Column(db.Integer())
    tasks = db.relationship('TestTask', backref='test')
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))


class TestTask(db.Model):
    __tablename__ = 'test_tasks'
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(150))
    solve = db.Column(db.Integer())
    count = db.Column(db.Integer())
    task_id = db.Column(db.Integer(), db.ForeignKey('subjects_tasks.id'))
    test_id = db.Column(db.Integer(), db.ForeignKey('test_solve.id'))