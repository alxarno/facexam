from run import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)


    def __init__(self, username, email):
        self.nickname = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.nickname)