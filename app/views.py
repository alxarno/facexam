from app import app, db, models
from flask import redirect, url_for, request, jsonify

@app.route('/')
def home():
    return  redirect(url_for('login'))

@app.route('/mypage')
def userpage():
    return app.send_static_file('frontend/EnterpriseUser/index.html')

@app.route('/<subject>')
def subjectpage(subject):
    return app.send_static_file('frontend/EnterpriseUser/index.html')

@app.route('/<subject>/lection/<int:lessonid>')
@app.route('/<subject>/lection/')
@app.route('/<subject>/lection')
@app.route('/<subject>/test/<int:lessonid>')
@app.route('/<subject>/test/')
@app.route('/<subject>/test')
def lectionsPage(subject, lessonid=None):
    return redirect(url_for('subjectpage', subject=subject))


@app.route('/login')
def login():
    return app.send_static_file('frontend/EnterpriseLogin/index.html')

@app.route('/api/enter')
def enter():
    loginUser = request.args.get('login', 0, type=str)
    passwordUser = request.args.get('pass', 0, type=str)
    if(loginUser=='jesus' and passwordUser == '1111'):
        return jsonify(result='/mypage')
    else:
        return jsonify(result='Error')
#
#
#
@app.route('/redactor')
def redactor():
    return redirect(url_for('static', filename='frontend/EnterpriseUser/index.html'))

@app.route('/api/createperson')
def createperson():
    users = models.User(nickname='susan', email='susan@email.com')
    db.session.add(users)
    db.session.commit()
    return jsonify(result='good')


@app.route('/api/getpersons')
def getperson():
    users = models.User.query.all()
    finishArray = []
    for u in users:
        nameU = u.nickname
        idU = u.id
        time = {idU: nameU}
        finishArray.append(time)
    return jsonify(finishArray)


# @app.route('/api/test', methods=['GET', 'OPTIONS'])
# def test():
#     jesus = "Congratulations, api is work @facexem_api. Time is ("+time.ctime(time.time())+')'
#     return jsonify(jesus)

