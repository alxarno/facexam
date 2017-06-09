from datetime import datetime
import random, hashlib, time, json, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, redirect, url_for, request, jsonify, session

from .models import User, TestUser, UserPage,  UserActivity, SubjectStatic
from ..extensions import db
from ..subject.models import Subject, Task, Challenge, Content, Issue, TaskSolve, SessionTasks
from .methods import somefuncs, user_page_funcs, subject_page_funcs
from ..achievements.models import Achievement

user = Blueprint('user', __name__, url_prefix='/api/user')


def verif_user():
    try:
        data = json.loads(request.data)
        user_token = data['token']
        maybe_user = User.query.filter_by(token=user_token).first()
        if maybe_user:
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
                            user_achievements=json.dumps([]), user_active_background='/bg/wall1')
            db.session.add(info)
            count = 0
            for i in subjects:
                if count > 3:
                    continue
                subject = Subject.query.filter_by(codename=i).first()
                if subject:
                    user_static_subject = SubjectStatic(subject_codename=i, user=user, date_reload=0,\
                                                        test_points=0, last_random_task_time=0, best_session_list=0)
                    db.session.add(user_static_subject)
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
        return jsonify(session['token'])
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
    now_user = verif_user()
    if now_user:
        try:
            data = json.loads(request.data)
            codename = data['subject']
            type = data['type']
        except:
            return jsonify(result='Error')
        if type == 'singletask':
            number = data['number']
        else:
            number = 'any'
        if user:
            subject = Subject.query.filter_by(codename=codename).first()
            solve_task_array = []
            users_solve_tasks = db.session.query(TaskSolve).filter(TaskSolve.user_id == now_user.id)
            users_solve_tasks = users_solve_tasks.join(Task, Task.id == TaskSolve.task_id)
            users_solve_tasks = users_solve_tasks.join(Subject, Subject.id == Task.subject_id).all()
            for taskSolve in users_solve_tasks:
                solve_task_array.append(taskSolve.task_id)
            if number == 'any':
                tasks = db.session.query(Task).filter(Task.subject_id == subject.id,
                                                      ~Task.id.in_(solve_task_array)).limit(20).all()
                if len(tasks) == 0:
                    if len(solve_task_array)==0:
                        return jsonify(result="Empty")
                    tasks = db.session.query(Task).filter(Task.subject_id == subject.id,
                                            Task.id != solve_task_array[len(solve_task_array)-1]).limit(20).all()
            else:
                tasks = db.session.query(Task).filter(Task.subject_id == subject.id,
                                                      Task.number == number,
                                                      ~Task.id.in_(solve_task_array)).limit(20).all()
                if len(tasks) == 0:
                    if len(solve_task_array)==0:
                        return jsonify(result="Empty")
                    tasks = db.session.query(Task).filter(
                        Task.subject_id == subject.id,
                        Task.number == number,
                        Task.id != solve_task_array[len(solve_task_array)-1]).limit(20).all()
            if len(tasks) > 0:
                num_rnd_task = random.randint(0, len(tasks)-1)
                final_task = tasks[num_rnd_task]
                content = Content.query.filter_by(id=final_task.id).first()
                final_task = {'id': final_task.id, 'content': json.loads(content.content)}
                return jsonify(final_task)
            else:
                return jsonify(result="Empty")
    else:
        return jsonify(result='Error')


@user.route('/get_answer', methods=['POST'])
def get_answer():
    now_user = verif_user()
    if now_user:
        try:
            data = json.loads(request.data)
            id = data['id']
            answers = data['answers']
            user_time = data['time']
            type = data['type']
            session_key = data['session_key']
        except:
            return jsonify(result='Error')
        content = Content.query.filter_by(id=id).first()
        right = False
        solve = 0
        all_time = time.time()
        curent_answer = json.loads(content.answers)
        count= 0
        for i in range(len(answers)):
            if answers[i] == curent_answer[i]:
                count += 1
        if count >= 1:
            right = True
            solve = 1
        #type
        if type == 'singletask':
            type = 1
        elif type == 'randomtask':
            type = 2
        session_task = SessionTasks.query.filter_by(key=session_key, user_id=now_user.id).first()
        if session_task:
            task_solve = TaskSolve(time=user_time, count=count, solve=solve, alltime=all_time,
                                  user_id=now_user.id, task_id=content.task_id, type=type, session_id=session_task.id)
            db.session.add(task_solve)
            db.session.commit()
            # for i in range
            return jsonify(answer=right)
    return jsonify(result='Error')


@user.route('/session_start', methods=['POST'])
def set_session_start():
    user = verif_user()
    if user:
        try:
            data = json.loads(request.data)
            codename = data['subject']
            subject = Subject.query.filter_by(codename=codename).first()
            if subject:
                time_now = time.time()
                key = hashlib.md5(str(User.id).encode('utf8')+str(time_now).encode('utf8')).hexdigest()
                session = SessionTasks(date=time_now, user_id=user.id, key=key, subject_id=subject.id)
                db.session.add(session)
                db.session.commit()
                return jsonify(key)
        except:
            return jsonify(result='Error')
    return jsonify(result='Error')


@user.route('/set_report_task', methods=['POST'])
def set_report_task():
    user = verif_user()
    if user:
        try:
            data = json.loads(request.data)
            id = data['id']
            content = data['content']
        except:
            return jsonify(result='Error')
        task = Task.query.filter_by(id=id).first()
        if task:
            report = Issue(content=content, solve=0, author_id=user.id, task_id=id)
            db.session.add(report)
            db.session.commit()
            return jsonify(result='Success')
    return jsonify(result='Error')


@user.route('/get_description', methods=['POST'])
def get_description():
    now_user = verif_user()
    if now_user:
        try:
            data = json.loads(request.data)
            id = data['id']
        except:
            return jsonify(result='Error')
        content = Content.query.filter_by(id=id).first()
        return content.description
    else:
        return jsonify(result='Error')


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
            # task_solve = TaskSolve()
            # somefuncs.set_activity_user(user_activities, user, 'task')
            # somefuncs.reg_achievements_progress('task', user)
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


# @user.route('/get_test', methods=['POST'])
# def get_test():
#     now_user = verif_user()
#     if now_user:
#         data = json.loads(request.data)
#         test = []
#         try:
#             info_counts = data['counts']
#             subject = data['subject_codename']
#         except:
#             return jsonify(result="Error: havent counts or subject_codename")
#         subject = Subject.query.filter_by(codename=subject).first()
#         if subject:
#             for count in info_counts:
#                 now_count_tasks = int(info_counts[count]['count'])
#                 tasks_id = []
#                 limit = 0
#                 for g in range(0, now_count_tasks):
#                     task_count = int(Task.query.filter_by(subject_id=subject.id).count())
#                     random1 = random.random()
#                     random_id_task = round(task_count*random1)
#                     if random_id_task not in tasks_id:
#                         rt = Task.query.filter_by(id=random_id_task, number=count, subject_id=subject.id).first()
#                         if rt:
#                             tasks_id.append(random_id_task)
#                             test.append({"id": rt.id, "content": rt.content})
#                     else:
#                         if limit <= 3:
#                             now_count_tasks += 1
#                             limit += 1
#             return jsonify(test)
#         else:
#             return jsonify(result="Error: bad subject_codename")
#     else:
#         return jsonify(result="Error")


# @user.route('/check_test', methods=['POST'])
# def check_test():
#     now_user = verif_user()
#     points = 0
#     if now_user:
#         data = json.loads(request.data)
#         try:
#             answers = data['answers']
#             type = data['type']
#             subject_codename = data['subject_code']
#         except:
#             return jsonify(result="Error")
#         for i in answers:
#             now_id = i.id
#             type = i.type
#             answer = i.answer
#             task = Task.query.filter_by(id=now_id).first()
#             try:
#                 real_answer = json.loads(task.answer)
#             except:
#                 return jsonify(result="Error")
#             if task:
#                 if type == 'hard':
#                     for j in range(0, len(answer)-1):
#                         if answer[j] == real_answer[j]:
#                             points += 1
#                 else:
#                     if answer[0] == real_answer[0]:
#                         points += 1
#         if type == 'usual':
#             subject = UserSubjects.query.filter_by(subject_codename=subject_codename).first()
#             real_subject = Subject.query.filter_by(codename=subject_codename).first()
#             if subject and real_subject:
#                 tests = json.loads(subject.passed_tests)
#                 tests[len(tests)-1] = 0
#                 for i in range(1, len(tests)-1, -1):
#                     tests[i] = tests[i-1]
#                 system_points = json.loads(real_subject.system_points)
#                 points_100 = system_points[str(points)]
#                 tests[0] = points_100
#                 subject.points_of_tests = tests
#                 db.session.dommit()
#         return jsonify(result=points)
#     else:
#         return jsonify(result='Error')


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
        subject = Subject.query.filter_by(codename=subject_codename).first()
        if subject:
            result = subject_page_funcs.get_subject_activity(now_user, subject)
            subject_page_funcs.task_info(now_user, subject)
            return jsonify(result)
    return 'Error'


@user.route('/get_my_subject', methods=['POST'])
def get_my_subject():
    now_user = verif_user()
    if now_user:
        data = json.loads(request.data)
        try:
            subject_codename = data['subject']
        except:
            return jsonify(result='Error')
        subject = Subject.query.filter_by(codename=subject_codename).first()
        if subject:
            task_info = subject_page_funcs.task_info(now_user, subject)
            activity = subject_page_funcs.get_subject_activity(now_user, subject)
        return jsonify({"task_info": task_info, "activity": activity})
    return jsonify(result='Error')


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


@user.route('/get_my_settings', methods=['POST'])
def get_settings():
    user = verif_user()
    if user:
        return jsonify({'key': user.public_key})
    else:
        return jsonify(result='Error')