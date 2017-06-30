import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
UPLOAD_FOLDER = './frontend/other/achievements'
# SUBJECT_FOLDER = './frontend/other/tasks'
SUBJECT_FOLDER = './frontend/other/subjects_pic'
TASK_FOLDER = './frontend/other/tasks'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
SECRET_KEY = '27833c3ffb0ab43cf45564ca427fe630'
ADMIN_KEY = '232323'
AUTHOR_KEY = '232323'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True