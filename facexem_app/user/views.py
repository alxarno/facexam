import datetime
import time
import json

from flask import Blueprint, redirect, url_for, request, jsonify, session

from .models import User, TestUser, UserPage, UserSubjects, UserActivity, UserNotifications
from ..extensions import db
from ..subject.models import Subject, Lection

user = Blueprint('user', __name__, url_prefix='/api/user')


def verif_user():
    try:
        data = json.loads(request.data)
        user_token = data['token']
        maybe_user = User.query.filter_by(token=user_token).first()
        return maybe_user
    except:
        return False


@user.route('/create', methods=['POST'])
def create_user():
    try:
        data = json.loads(request.data)
        email = data['email']
    except:
        return jsonify(result="Error")
    current_email = User.query.filter_by(email=email).first()
    if current_email is None:
        new_test_user = TestUser(email)
        db.session.add(new_test_user)
        db.session.commit()
        return jsonify(result=new_test_user.key)
    else:
        return jsonify(result="Error")


@user.route('/prove_email', methods=['POST'])
def prove_email():
    try:
        data = json.loads(request.data)
        email = data['email']
        name = data['name']
        key = data['key']
        password = data['pass']
    except:
        return jsonify(result="Error")
    created_user = TestUser.query.filter_by(key=key).first()
    if created_user:
        if created_user.email == email:
            new_user = User(name, password, email)
            db.session.add(new_user)
            token = new_user.token
            session['token'] = token
            session.pop('test_email', None)
            info = UserPage(photo='', about='', user_active_achivs='', user=new_user, last_lections=json.dumps([]))
            db.session.add(info)
            TestUser.query.filter_by(email=email).delete()
            db.session.commit()
            print("User " + name + " is created")
            return jsonify(result="Success")
        else:
            return jsonify(result='Bad email')
    else:
        return jsonify(result="Bad key")


@user.route('/delete', methods=['POST'])
def delete_user():
    current_user = verif_user()
    if current_user:
        # deleting user's information
        page = current_user.info_page[0]
        UserPage.query.filter_by(id=page.id).delete()
        # deleting user's subjects
        subjects = current_user.info_subjects
        for sub in subjects:
            Subject.query.filter_by(id=sub.id).delete()
        # deleting user's notifications
        notifications = current_user.notifications
        for notif in notifications:
            UserNotifications.query.filter_by(id=notif.id).delete()
        # deleting user's activity
        activity = current_user.activity
        for day in activity:
            UserActivity.query.filter_by(id=day.id).delete()
        # deleting user
        name = current_user.name
        data = json.loads(request.data)
        user_token = data['token']
        User.query.filter_by(token=user_token).delete()
        db.session.commit()
        print('User ' + name + ' is deleted')
        return jsonify(result='Success')
    else:
        return jsonify(result="Error")


@user.route('/get_token', methods=['POST'])
def get_token():
    if 'token' in session:
        return jsonify(result=session['token'])
    else:
        return redirect(url_for('login'))


@user.route('/login', methods=['POST'])
def login_user():
    if 'token' in session:
        return jsonify(result="Success")
    else:
        try:
            data = json.loads(request.data)
            email = data['email']
            password = data['pass']
        except:
            return jsonify(result="Error")
        possible_user = User.query.filter_by(email=email).first()
        if possible_user:
            if possible_user.check_password(password):
                token = possible_user.token
                session['token'] = token
                return jsonify(result="Success")
            else:
                return jsonify(result="Error")
        else:
            return jsonify(result="Error")


@user.route('/logout', methods=['POST', "GET"])
def logout():
    if 'token' not in session:
        return jsonify(result="Error")
    else:
        session.pop('token', None)
        return redirect(url_for('login'))


@user.route('/get_page_info', methods=['POST'])
def get_page_info():
    maybe_user = verif_user()
    if maybe_user:
        info = maybe_user.info_page
        photo = info[0].photo
        about = info[0].about
        achivs = json.loads(info[0].user_active_achivs)
        background = info[0].user_active_background
        finish = [{'photo': photo, 'about': about, 'achivs': achivs, 'background': background}]
        return jsonify(finish)
    else:
        return jsonify(result='Error')


@user.route('/set_page_info', methods=['POST'])
def set_page_info():
    data = json.loads(request.data)
    maybe_user = verif_user()
    if maybe_user:
        info = maybe_user.info_page
        info[0].photo = data['photo']
        info[0].about = data['about']
        achivs = json.dumps(data['achivs'])
        backgrs = data['background']
        info[0].user_active_achivs = achivs
        info[0].user_active_background = backgrs
        db.session.commit()
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")


@user.route('/set_subjects', methods=['POST'])
def set_subjects():
    data = json.loads(request.data)
    codenames = data['codenames']
    maybe_user = verif_user()
    if maybe_user:
        for name in codenames:
            user_subject = UserSubjects(subject_codename=name, passed_lections=json.dumps([]),
                                        passed_tests='', experience=0,
                                        points_of_tests='', user=maybe_user)
            db.session.add(user_subject)
        db.session.commit()
        return jsonify(result="Success")
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_subjects', methods=['POST'])
def get_subjects():
    maybe_user = verif_user()
    if maybe_user:
        subjects = maybe_user.info_subjects
        result = []
        for s in subjects:
            subject = {'codename': s.subject_codename,
                       'lections': s.passed_lections,
                       'tests': s.passed_tests,
                       'points': s.points_of_tests,
                       'experience': s.experience}
            result.append(subject)
        return jsonify(result)
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_lections', methods=['POST'])
def get_lections():
    data = json.loads(request.data)
    subject_code_name = data['subject_code_name']
    users_lections = verif_user()
    true_subject = ''
    for subject in users_lections.info_subjects:
        if subject.subject_codename == subject_code_name:
            true_subject = subject
    if true_subject != '':
        if true_subject.passed_lections != '':
            users_lections = json.loads(true_subject.passed_lections)
        else:
            users_lections = []
        current_subject = Subject.query.filter_by(codename=subject_code_name).first()
        if current_subject:
            themes = current_subject.themes
            theme = []
            number_theme = 1
            for j in themes:
                lections = j.lections
                lections_final = []
                number = 0
                for k in lections:
                    if str(k.id) in users_lections:
                        lection = {'name': k.name, 'description': k.description, 'link': '/lection/' + str(k.id),
                                   'number': number, 'type': k.type, 'theme': number_theme, 'done': True}
                    else:
                        lection = {'name': k.name, 'description': k.description, 'link': '/lection/' + str(k.id),
                                   'number': number, 'type': k.type, 'theme': number_theme}
                    number += 1
                    lections_final.append(lection)
                number_theme += 1
                theme.append({'name': j.name, 'lections': lections_final})
            return jsonify(theme)
        else:
            return jsonify(result='Error')
    else:
        return jsonify(result='Error')


@user.route('/set_view_lection', methods=['POST'])
def set_view_lection():
    data = json.loads(request.data)
    subject_code_name = data['subject_code_name']
    lection_id = data['lection_id']
    now_user = verif_user()
    now_time = time.localtime()
    user_activities = now_user.activity
    real_activ = ''
    if user_activities:
        for activ in user_activities:
            if activ.date == datetime.time(now_time.tm_year, now_time.tm_mon, now_time.tm_mday):
                real_activ = activ
    if real_activ == '':
        real_activ = UserActivity(date=datetime.date(now_time.tm_year, now_time.tm_mon, now_time.tm_mday),
                                  lections=0, user=now_user)
        db.session.add(real_activ)
        db.session.commit()
    true_subject = ''
    for subject in now_user.info_subjects:
        if subject.subject_codename == subject_code_name:
            true_subject = subject
    if now_user:
        if true_subject != '':
            if true_subject.passed_lections != '':
                passed_lections = json.loads(true_subject.passed_lections)
            else:
                passed_lections = []
            real_activ.lections += 1
            passed_lections.append(lection_id)
            true_subject.passed_lections = json.dumps(passed_lections)
            db.session.commit()
            return jsonify(result="Success")
        else:
            return jsonify(result='Error: user are havent this subject')
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_progress', methods=['POST'])
def get_progress():
    now_user = verif_user()
    if now_user:
        subjects = now_user.info_subjects
        if subjects:
            final = []
            for subject in subjects:
                subject_code = subject.subject_codename
                lections = len(json.loads(subject.passed_lections))
                real_subject = Subject.query.filter_by(codename=subject_code).first()
                name = real_subject.name
                count_lections = 0
                for theme in real_subject.themes:
                    count_lections += len(theme.lections)
                if count_lections == 0:
                    final.append({name: 0})
                else:
                    final.append({name: (lections / count_lections) * 100})
            return jsonify(final)
        else:
            return jsonify(result='Error: user are havent this subject')
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_activity', methods=['POST'])
def get_activity():
    now_user = verif_user()
    now_time = time.localtime()
    now_date = datetime.date(now_time.tm_year, now_time.tm_mon, now_time.tm_mday)
    final = []
    # creating array with last 7 days dates
    dates = []
    i = 6
    while i >= 0:
        date = now_date - datetime.timedelta(days=i)
        dates.append(str(date))
        i -= 1
    if now_user:
        user_activities = now_user.activity
        # test, is day of activity in last 7 days
        for day in user_activities:
            if str(day.date) in dates:
                final.append(day.lections)
        if len(final) < 7:
            times = len(final)
            while times < 7:
                final.append(0)
                times += 1
        final = list(reversed(final))
        return jsonify(final, dates)
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/change_design', methods=['POST'])
def change_design():
    data = json.loads(request.data)
    users_data = data['user_data']
    now_user = verif_user()
    if now_user:
        user_settings = now_user.info_page[0]
        now_user.name = users_data['name']
        user_settings.photo = users_data['photo']
        user_settings.about = users_data['about']
        user_settings.user_active_achivs = json.dumps(users_data['achivs'])
        user_settings.user_active_background = users_data['background']
        db.session.commit()
        return jsonify(result="Success")
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_notifications', methods=['POST'])
def get_notifications():
    now_user = verif_user()
    result = []
    if now_user:
        notifics = now_user.notifications
        if notifics:
            for notif in notifics:
                author = User.query.get(notif.author)
                author_photo = author.info_page[0].photo
                notif = {'author': author.name,
                         'authorPhoto': author_photo,
                         'text': notif.text,
                         'type': notif.type}
                result.append(notif)
            return jsonify(result)
        else:
            return jsonify(result)
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_last_lections', methods=['POST'])
def get_last_lections():
    now_user = verif_user()
    if now_user:
        lections = now_user.info_page[0].last_lections
        return lections
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_lection', methods=['POST'])
def get_lection():
    data = json.loads(request.data)
    lection_id = data['lection_id']
    now_user = verif_user()
    if now_user:
        last_lections = json.loads(now_user.info_page[0].last_lections)
        if lection_id not in last_lections:
            result_last_lections = [lection_id]
            for i in range(6):
                if len(last_lections) > i:
                    result_last_lections.append(last_lections[i])
                else:
                    break
            now_user.info_page[0].last_lections = json.dumps(result_last_lections)
            db.session.commit()
        lection = Lection.query.get(lection_id)
        if lection:
            result = {'name': lection.name,
                      'content': json.loads(lection.content)}
            return jsonify(result=result)
        else:
            return jsonify(result='Fail this lection is havent')
    else:
        return jsonify(result='Fail this token is havent')



