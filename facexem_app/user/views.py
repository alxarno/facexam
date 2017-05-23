import datetime
import time
import json
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, redirect, url_for, request, jsonify, session

from .models import User, TestUser, UserPage, UserSubjects, UserActivity
from ..extensions import db
from ..subject.models import Subject, Task, Challenge, Content
from .methods import somefuncs, user_page_funcs, subject_page_funcs
from ..achievements.models import Achievement

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
    already = TestUser.query.filter_by(email=email).first()
    if already:
        db.session.delete(already)
        db.session.commit()
    if current_email is None:
        new_test_user = TestUser(email)
        db.session.add(new_test_user)
        db.session.commit()
        me  = 'facile.exem@gmail.com'
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Подтверждение почты Facexem'
        msg['From'] = me
        msg['To'] = email

        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               How are you?<br>
               Here is the <a href="http://127.0.0.1/prove-email/">prove email</a> you wanted.
            </p>
          </body>
        </html>
        """
        part = MIMEText(html, 'html')
        msg.attach(part)
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login('facile.exem@gmail.com', 'e710bf70dd906bebaa0b66982eb6e90c')
        smtpObj.sendmail(me, email, msg.as_string())
        smtpObj.quit()
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
            # info = UserPage(photo='', about='', user_active_achivs='', user=new_user, city='', experience=0)
            # db.session.add(info)
            TestUser.query.filter_by(email=email).delete()
            db.session.commit()
            print("User " + name + " is created")
            return jsonify(result="Success")
        else:
            return jsonify(result='Bad email')
    else:
        return jsonify(result="Bad key")


@user.route('/done_create_page', methods=['POST'])
def done_create_page():
    user = verif_user()
    if user:
        if user.profile_done == 0:
            try:
                data = json.loads(request.data)
                city = data['city']
                about = data['about']
                subjects = data['subjects']
            except:
                return jsonify(result="Error")
            info = UserPage(photo='jeorge', city=city, about=about,
                            user_active_achivs=json.dumps([]), user=user, experience=0, last_actions=json.dumps([]),
                            user_achievements = json.dumps([]), user_active_background='/bg/wall1')
            db.session.add(info)
            count = 0
            for i in subjects:
                if count > 3:
                    continue
                subject = Subject.query.filter_by(codename=i).first()
                if subject:
                    user_subject = UserSubjects(subject_codename=i, passed_lections=json.dumps([]),\
                                 passed_tests=json.dumps([]), experience=0, activity=json.dumps([]),\
                                 points_of_tests=0, user=user, now_challenge=json.dumps([]))
                    db.session.add(user_subject)
                    count += 1
            user.profile_done = 1
            db.session.commit()
            return jsonify(result="Success")
        else:
            return jsonify(result="Error")
    else:
        return jsonify(result="Error")


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
        return jsonify(result='Error')


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


@user.route('/logout', methods=['GET', 'POST'])
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
        return jsonify(user_page_funcs.user_get_page_info(maybe_user))
    else:
        return jsonify(result='Error')


@user.route('/set_page_info', methods=['POST'])
def set_page_info():
    data = json.loads(request.data)

    maybe_user = verif_user()
    if maybe_user:
        info = maybe_user.info_page
        try:
            photo = data['photo']
            info[0].photo = photo
        except:
            photo = 0
        try:
            name = data['name']
            maybe_user.name = name
        except:
            name = 0
        try:
            city = data['city']
            info[0].city = city
        except:
            city = 0
        try:
            about = data['about']
            info[0].about = about
        except:
            about = 0
        try:
            achivs = json.dumps(data['achivs'])
            info[0].user_active_achivs = achivs
        except:
            achivs = 0
        try:
            backgrs = data['background']
            info[0].user_active_background = backgrs
        except:
            backgrs = 0
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
        return jsonify(user_page_funcs.user_get_subjects(maybe_user))
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_all_subjects', methods=['POST'])
def get_all_subjects():
    user = verif_user()
    if user:
        final = []
        db.session.commit()
        subjects = Subject.query.all()
        for s in subjects:
            if s.access == 1:
                final.append({"name": s.name, "codename": s.codename})
        return jsonify(final)
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
    if now_user:
        return jsonify(user_page_funcs.user_get_activity(now_user))
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
    if now_user:
        return jsonify(user_page_funcs.user_get_notifications(now_user))
    else:
        return jsonify(result='Fail this token is havent')


@user.route('/get_last_actions', methods=['POST'])
def get_last_actions():
    now_user = verif_user()
    if now_user:
        return jsonify(user_page_funcs.user_get_last_actions(now_user))
    else:
        return jsonify(result='Fail this token is havent')


# @user.route('/get_lection', methods=['POST'])
# def get_lection():
#     data = json.loads(request.data)
#     lection_id = data['lection_id']
#     now_user = verif_user()
#     if now_user:
#         last_lections = json.loads(now_user.info_page[0].last_lections)
#         if lection_id not in last_lections:
#             result_last_lections = [lection_id]
#             for i in range(6):
#                 if len(last_lections) > i:
#                     result_last_lections.append(last_lections[i])
#                 else:
#                     break
#             now_user.info_page[0].last_lections = json.dumps(result_last_lections)
#             db.session.commit()
#         lection = Lection.query.get(lection_id)
#         if lection:
#             result = {'name': lection.name,
#                       'content': json.loads(lection.content)}
#             return jsonify(result=result)
#         else:
#             return jsonify(result='Fail this lection is havent')
#     else:
#         return jsonify(result='Fail this token is havent')


@user.route('/get_task', methods=['POST'])
def get_task():
    data = json.loads(request.data)
    try:
        codename = data['subject']
        type =data['type']
    except:
        return jsonify(result='Error')
    if type == 'singletask':
        number = data['number']
    else:
        number = 'any'
    if user:
        subject = Subject.query.filter_by(codename=codename).first()
        if number == 'any':
            tasks = Task.query.filter_by(subject_id=subject.id).limit(20).all()
        else:
            tasks = Task.query.filter_by(subject_id=subject.id, number=number).limit(20).all()
        if len(tasks) > 0:
            num_rnd_task = random.randint(0, len(tasks)-1)
            final_task = tasks[num_rnd_task]
            content = Content.query.filter_by(id=final_task.id).first()
            final_task = {'id': final_task.id, 'content': json.loads(content.content)}
            return jsonify(final_task)
        else:
            return jsonify(result="Empty")
    else:
        return jsonify(result='Hello')


@user.route('/get_answer', methods=['POST'])
def get_answer():
    data = json.loads(request.data)

    return jsonify(result='Hello')


@user.route('/check_task', methods=['POST'])
def check_task():
    user = verif_user()
    data = json.loads(request.data)
    try:
        task_id = data['task_id']
        answer = data['answer']
    except:
        return jsonify(result='Error')
    if user:
        task = Task.query.filter_by(id=task_id).first()
        user_activities = user.activity
        real_answer = json.loads(task.answer)
        count_answers = len(real_answer)
        right = 0
        for i in range(0, count_answers):
                if real_answer[i] == answer[i]:
                    right += 1

        if right > 0:
            sent = True
            somefuncs.set_activity_user(user_activities, user, 'task')
            somefuncs.reg_achievements_progress('task', user)
        else:
            sent = False
        return jsonify({'user_answer': answer, 'right': sent, 'description': task.description})
    else:
        return jsonify(result="Error")


@user.route('/get_achievements', methods=['POST'])
def get_achieves():
    user = verif_user()
    if user:
        try:
            user_achievs = json.loads(user.info_page[0].user_achievements)
        except:
            user_achievs = []
        try:
            user_active_achiev = json.loads(user.info_page[0].user_active_achivs)
        except:
            user_active_achiev = []
        achievements = Achievement.query.all()
        final = []
        for ach in achievements:
            if str(ach.id) in user_active_achiev:
                choose = True
            else:
                choose = False
            now = {'name': ach.name,
                   'content': ach.content,
                   'max': ach.max,
                   'img': 'achiev/'+str(ach.id),
                   'choose': choose}
            try:
                now['now'] = user_achievs[str(ach.id)]['now']
            except:
                now['now'] = 0
            final.append(now)
        return jsonify(final)
    else:
        return jsonify(result="Error")


@user.route('/get_global_static', methods=['POST'])
def global_static():
    now_user = verif_user()
    if now_user:
        result = user_page_funcs.user_get_global_static(now_user)
        if result:
            return jsonify(result)
        else:
            return jsonify(result="Error")
    else:
        return jsonify(result="Error")


@user.route('/get_test', methods=['POST'])
def get_test():
    now_user = verif_user()
    if now_user:
        data = json.loads(request.data)
        test = []
        try:
            info_counts = data['counts']
            subject = data['subject_codename']
        except:
            return jsonify(result="Error: havent counts or subject_codename")
        subject = Subject.query.filter_by(codename=subject).first()
        if subject:
            for count in info_counts:
                now_count_tasks = int(info_counts[count]['count'])
                tasks_id = []
                limit = 0
                for g in range(0, now_count_tasks):
                    task_count = int(Task.query.filter_by(subject_id=subject.id).count())
                    random1 = random.random()
                    random_id_task = round(task_count*random1)
                    if random_id_task not in tasks_id:
                        rt = Task.query.filter_by(id=random_id_task, number=count, subject_id=subject.id).first()
                        if rt:
                            tasks_id.append(random_id_task)
                            test.append({"id": rt.id, "content": rt.content})
                    else:
                        if limit <= 3:
                            now_count_tasks += 1
                            limit += 1
            return jsonify(test)
        else:
            return jsonify(result="Error: bad subject_codename")
    else:
        return jsonify(result="Error")


@user.route('/check_test', methods=['POST'])
def check_test():
    now_user = verif_user()
    points = 0
    if now_user:
        data = json.loads(request.data)
        try:
            answers = data['answers']
            type = data['type']
            subject_codename = data['subject_code']
        except:
            return jsonify(result="Error")
        for i in answers:
            now_id = i.id
            type = i.type
            answer = i.answer
            task = Task.query.filter_by(id=now_id).first()
            try:
                real_answer = json.loads(task.answer)
            except:
                return jsonify(result="Error")
            if task:
                if type == 'hard':
                    for j in range(0, len(answer)-1):
                        if answer[j] == real_answer[j]:
                            points += 1
                else:
                    if answer[0] == real_answer[0]:
                        points += 1
        if type == 'usual':
            subject = UserSubjects.query.filter_by(subject_codename=subject_codename).first()
            real_subject = Subject.query.filter_by(codename=subject_codename).first()
            if subject and real_subject:
                tests = json.loads(subject.passed_tests)
                tests[len(tests)-1] = 0
                for i in range(1, len(tests)-1, -1):
                    tests[i] = tests[i-1]
                system_points = json.loads(real_subject.system_points)
                points_100 = system_points[str(points)]
                tests[0] = points_100
                subject.points_of_tests = tests
                db.session.dommit()
        return jsonify(result=points)
    else:
        return jsonify(result='Error')


@user.route('/get_challenge', methods=['POST'])
def get_challenge():
    now_user = verif_user()
    if now_user:
        data = json.loads(request.data)
        try:
            subject_codename = data['subject_codename']
        except:
            return jsonify(result='Error')
        subject = False
        for i in now_user.info_subjects:
            if i.subject_codename == subject_codename:
                subject = i
        if subject:
            try:
                challenge = json.loads(subject.now_challenge)
            except:
                challenge = somefuncs.add_challenge(now_user, subject)
            if challenge:
                real_challenge = Challenge.query.filter_by(id=challenge[0]).first()
                if real_challenge:
                    content = real_challenge.content
                    now = challenge[1]
                    max = real_challenge.max
                    prize = real_challenge.prize
                    return jsonify({'content': content,
                                    'now': now,
                                    'max': max,
                                    'prize': prize})
                else:
                    return jsonify(result='Error')
            else:
                return jsonify(result='Error')
        else:
            return jsonify(result="Error")
    else:
        return jsonify(result='Error')


@user.route('/get_preference', methods=['POST'])
def get_preference():
    user = verif_user()
    if user:
        return jsonify(user_page_funcs.user_get_preference(user))
    else:
        return jsonify(result='Error')


@user.route('/get_activity_subject', methods=['POST'])
def get_subject_activity():
    now_user = verif_user()
    if now_user:
        data = json.loads(request.data)
        try:
            subject_codename = data['subject']
        except:
            return jsonify(result="Error")
        result = subject_page_funcs.get_subject_activity(now_user, subject_codename)
        return jsonify(result)
    else:
        return 'Error'


@user.route('/get_mypage', methods=['POST'])
def get_mypage():
    now_user = verif_user()
    if now_user:
        funcs = user_page_funcs
        user_page_info = funcs.user_get_page_info(now_user)
        user_subjects = funcs.user_get_subjects(now_user)
        user_activity = funcs.user_get_activity(now_user)
        user_preference = funcs.user_get_preference(now_user)
        user_last_actions = funcs.user_get_last_actions(now_user)
        user_global_static = funcs.user_get_global_static(now_user)
        final = {"info": user_page_info, "subjects": user_subjects, "activity": user_activity,
                 "preference": user_preference, "actions": user_last_actions,
                 "global_activ": user_global_static, "notifs": []}
        return jsonify(final)
    else:
        return jsonify(result='Error')
