from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from facexem_app.user.models import User
from facexem_app.user.constans import ROLES
from facexem_app.extensions import db
import os.path
db.create_all()
superuser = User(name='AlexArno', password='9f18cead', email='ledssssa@gmail.com',
                         role=ROLES['ADMIN'])
db.session.add(superuser)
db.session.commit()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))