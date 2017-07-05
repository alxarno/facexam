from datetime import datetime
import random, hashlib, time, json, smtplib, jwt, datetime, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, redirect, url_for, request, jsonify, session

from .models import User, TestUser, UserPage,  UserActivity, SubjectStatic, UserReport
from ..extensions import db
from ..subject.models import Subject, Task, Challenge, Content, Issue, TaskSolve, SessionTasks,TestSolve
from .methods import somefuncs, user_page_funcs, subject_page_funcs, user_test
from ..achievements.models import Achievement
from config import SECRET_KEY, USER_AVATARS
from functools import wraps
import urllib.request
import urllib.parse

user = Blueprint('user', __name__, url_prefix='/api/user')


def verification_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = json.loads(request.data)
        token = data['token']
        data_token = jwt.decode(token, SECRET_KEY)
        user_token = data_token['public']
        now_user = User.query.filter_by(token=user_token).first()
        if now_user:
            return f(now_user, *args, **kwargs)
        else:
            return jsonify({"result": 'Error', "type": 'User is required'})
    return wrapper


@user.route('/create', methods=['POST'])
def create_user():
    try:
        data = json.loads(request.data)
        email = data['email']
        name = data['name']
        password = data['pass']
    except:
        return jsonify(result="Error")
    current_email = User.query.filter_by(email=email).first()
    already = TestUser.query.filter_by(email=email).first()
    if already:
        db.session.delete(already)
        db.session.commit()
    if current_email is None:
        new_test_user = TestUser(email, name, password)
        db.session.add(new_test_user)
        db.session.commit()
        user = TestUser.query.filter_by(email=email).first()
        me = 'facile.exem@gmail.com'
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Подтверждение почты Facexem'
        msg['From'] = me
        msg['To'] = email
        link = "http://127.0.0.1:9999/api/user/prove-email/" +user.key
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               How are you?<br>
               Here is the <a href="""+link+""">prove email</a> you wanted.
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
        return jsonify(result="Success")
    else:
        return jsonify(result="Error")


@user.route('/vk', methods=['GET'])
def vk():
    code = request.args.get('code')
    app_id = '6101703'
    vk_secret = 'ZgSUUrBlC0bYfkxYILJS'
    redirect_url = "http://127.0.0.1:9999/api/user/vk"
    main_url = "https://api.vk.com/oauth/access_token?client_id="+app_id
    main_url += "&client_secret="+vk_secret+"&code="+code+"&redirect_uri="+redirect_url
    print(main_url)
    try:
        response = urllib.request.urlopen(main_url)
        answer = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return jsonify({'result': 'Error', 'type': 'Main auth vk is failed'})
    vk_access_token = answer['access_token']
    vk_uid = answer['user_id']
    user = User.query.filter_by(vk_id=vk_uid).first()
    if user:
        token = user.token
        key = jwt.encode({'public': token, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=43200)},
                         SECRET_KEY)
        session['token'] = key.decode('UTF-8')
        return redirect("http://127.0.0.1:9999/mypage")
    else:
        info_url = "https://api.vk.com/method/users.get?uids="+str(vk_uid)+"&access_token="+str(vk_access_token)+"&fields=uid,first_name,last_name"
        try:
            answer = urllib.request.urlopen(info_url)
            answer = json.loads(answer.read().decode("utf-8"))
        except:
            return jsonify({'result': 'Error', 'type': 'Get user vk is failed'})
        user_info = answer['response'][0]
        new_user = User(user_info['first_name']+' '+user_info['last_name'], None, None,None,vk_uid)
        db.session.add(new_user)
        db.session.commit()
        token = new_user.token
        token = jwt.encode({'public': token, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=43200)},
                           SECRET_KEY)
        session['token'] = token.decode('UTF-8')
        return redirect("http://127.0.0.1:9999/create-profile")



@user.route('/prove-email/<key>', methods=['GET'])
def prove_email(key):
    if key:
        created_user = TestUser.query.filter_by(key=key).first()
        if created_user:
            new_user = User(created_user.name, created_user.password, created_user.email)
            db.session.add(new_user)
            token = new_user.token
            token = jwt.encode({'public': token, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=43200)},
                             SECRET_KEY)
            session['token'] = token.decode('UTF-8')
            session.pop('test_email', None)
            TestUser.query.filter_by(key=key).delete()
            db.session.commit()
            return redirect("http://127.0.0.1:9999/create-profile", code=302)
        else:
            return redirect("http://127.0.0.1:9999/login", code=302)
    else:
        return redirect("http://127.0.0.1:9999/login", code=302)


@user.route('/done_create_page', methods=['POST'])
@verification_user
def done_create_page(now_user):
    # user = verif_user()
    user = now_user
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
                                                        test_points=0, last_random_task_time=0, solve_delete_tasks=0,
                                                        unsolve_delete_tasks=0, time_for_update=0,
                                                        last_tasks_hardest=json.dumps([]),
                                                        static_tasks_hardest=json.dumps([]), best_session_list=0)
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
                key = jwt.encode({'public': token, 'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=43200)},
                                 SECRET_KEY)
                session['token'] = key.decode('UTF-8')
                return jsonify({'token': key.decode('UTF-8')})
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
@verification_user
def get_page_info(now_user):
    return jsonify(user_page_funcs.user_get_page_info(now_user))


@user.route('/get_change_data', methods=['POST'])
@verification_user
def get_change_data(now_user):
    path = USER_AVATARS
    if os.path.exists(path):
        result = os.listdir(path)
        return jsonify(result)
    return jsonify({"result": 'Error', "type": 'Folder is required'})


@user.route('/set_page_info', methods=['POST'])
@verification_user
def set_page_info(now_user):
    data = json.loads(request.data)
    if now_user:
        info = now_user.info_page
        try:
            photo = data['photo']
            info[0].photo = photo
        except:
            photo = 0
        try:
            name = data['name']
            now_user.name = name
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
@verification_user
def get_subjects(now_user):
    return jsonify(user_page_funcs.user_get_subjects(now_user))


@user.route('/get_all_subjects', methods=['POST'])
@verification_user
def get_all_subjects(now_user):
    final = []
    db.session.commit()
    subjects = Subject.query.all()
    for s in subjects:
        if s.access == 1:
            final.append({"name": s.name, "codename": s.codename})
    return jsonify(final)


@user.route('/get_progress', methods=['POST'])
@verification_user
def get_progress(now_user):
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


@user.route('/get_activity', methods=['POST'])
@verification_user
def get_activity(now_user):
    return jsonify(user_page_funcs.user_get_activity(now_user))


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


@user.route('/get_last_actions', methods=['POST'])
@verification_user
def get_last_actions(now_user):
    return jsonify(user_page_funcs.user_get_last_actions(now_user))



@user.route('/get_task', methods=['POST'])
@verification_user
def get_task(now_user):
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
        # get user solve tasks id's list
        solve_task_array = []
        users_solve_tasks = db.session.query(TaskSolve).filter(TaskSolve.user_id == now_user.id)
        users_solve_tasks = users_solve_tasks.join(Task, Task.id == TaskSolve.task_id)
        users_solve_tasks = users_solve_tasks.join(Subject, Subject.id == Task.subject_id).all()
        for taskSolve in users_solve_tasks:
            solve_task_array.append(taskSolve.task_id)
        # make choosen of tasks without retrys
        if number == 'any':
            tasks = db.session.query(Task).filter(Task.subject_id == subject.id, Task.open == 1,
                                                      ~Task.id.in_(solve_task_array)).limit(20).all()
            if len(tasks) == 0:
                if len(solve_task_array) == 0:
                    return jsonify(result="Empty")
                tasks = db.session.query(Task).filter(Task.subject_id == subject.id, Task.open == 1,
                                            Task.id != solve_task_array[len(solve_task_array)-1]).limit(20).all()
        else:
            tasks = db.session.query(Task).filter(Task.subject_id == subject.id, Task.open == 1,
                                                      Task.number == number,
                                                      ~Task.id.in_(solve_task_array)).limit(20).all()
            if len(tasks) == 0:
                if len(solve_task_array) == 0:
                    return jsonify(result="Empty")
                tasks = db.session.query(Task).filter(
                    Task.open == 1,
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
@verification_user
def get_answer(now_user):
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
    return jsonify({"result": 'Error', "type": 'Session is failed'})


@user.route('/session_start', methods=['POST'])
@verification_user
def set_session_start(now_user):
    try:
        data = json.loads(request.data)
        codename = data['subject']
        codename = data['subject']
        subject = Subject.query.filter_by(codename=codename).first()
        if subject:
            time_now = time.time()
            key = hashlib.md5(str(now_user.id).encode('utf8')+str(time_now).encode('utf8')).hexdigest()
            session = SessionTasks(date=time_now, user_id=now_user.id, key=key, subject_id=subject.id)
            db.session.add(session)
            db.session.commit()
            return jsonify(key)
    except:
        return jsonify(result='Error')


@user.route('/set_report_task', methods=['POST'])
@verification_user
def set_report_task(now_user):
    try:
        data = json.loads(request.data)
        id = data['id']
        content = data['content']
    except:
        return jsonify(result='Error')
    task = Task.query.filter_by(id=id).first()
    if task:
        report = Issue(content=content, solve=0, author_id=now_user.id, task_id=task.id)
        db.session.add(report)
        db.session.commit()
        return jsonify(result='Success')


@user.route('/get_description', methods=['POST'])
@verification_user
def get_description(now_user):
    try:
        data = json.loads(request.data)
        id = data['id']
    except:
        return jsonify(result='Error')
    content = Content.query.filter_by(id=id).first()
    return content.description


@user.route('/check_task', methods=['POST'])
@verification_user
def check_task(now_user):
    data = json.loads(request.data)
    try:
        task_id = data['task_id']
        answer = data['answer']
    except:
        return jsonify(result='Error')
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



@user.route('/get_achievements', methods=['POST'])
@verification_user
def get_achieves(now_user):
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


@user.route('/get_global_static', methods=['POST'])
@verification_user
def global_static(now_user):
    result = user_page_funcs.user_get_global_static(now_user)
    if result:
        return jsonify(result)
    else:
        return jsonify(result="Error")


@user.route('/get_test', methods=['POST'])
@verification_user
def get_test(now_user):
    try:
        data =json.loads(request.data)
        counts = data['counts']
        subject = data['subject']
    except:
        return jsonify(result='Error')
    if counts == []:
        return jsonify(result='Error')
    subject = Subject.query.filter_by(codename=subject).first()
    if subject:
        final = []
        for i in range(len(counts)):
            final += user_test.get_user_task(now_user, subject, i+1, counts[i])
        return jsonify(final)


@user.route('/check-test', methods=['POST'])
@verification_user
def check_test(now_user):
    try:
        data = json.loads(request.data)
        answers = data['answers']
        time = data['time']
        codename = data['codename']
    except:
        return jsonify(result='Error')
    subject = Subject.query.filter_by(codename=codename).first()
    if subject:
        final = user_test.check_test(now_user, answers, subject, time)
        return jsonify(final)


@user.route('/test-result', methods=['POST'])
@verification_user
def test_result(now_user):
    try:
        data = json.loads(request.data)
        id = data['id']
        codename = data['codename']
    except:
        return jsonify(result='Error')
    test = TestSolve.query.filter_by(id=id, user_id=now_user.id).first()
    if test:
        subject = Subject.query.filter_by(codename=codename).first()
        if subject:
            final = user_test.get_test_results(now_user, test, subject)
            return jsonify(final)


@user.route('/get_preference', methods=['POST'])
@verification_user
def get_preference(now_user):
    return jsonify(user_page_funcs.user_get_preference(now_user))


@user.route('/get_activity_subject', methods=['POST'])
@verification_user
def get_subject_activity(now_user):
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


@user.route('/get_my_subject', methods=['POST'])
@verification_user
def get_my_subject(now_user):
    data = json.loads(request.data)
    try:
        subject_codename = data['subject']
    except:
        return jsonify(result='Error')
    subject = Subject.query.filter_by(codename=subject_codename).first()
    if subject:
        task_info = subject_page_funcs.task_info(now_user, subject)
        test_info = subject_page_funcs.get_tests_info(now_user, subject)
        activity = subject_page_funcs.get_subject_activity(now_user, subject)
    return jsonify({"task_info": task_info, "activity": activity, "test_info": test_info})


@user.route('/get_mypage', methods=['POST'])
@verification_user
def get_mypage(now_user):
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


@user.route('/get_my_settings', methods=['POST'])
@verification_user
def get_settings(now_user):
    return jsonify({'key': now_user.public_key, 'name': now_user.name})


@user.route('/get_test_info', methods=['POST'])
@verification_user
def get_test_info(now_user):
    try:
        data = json.loads(request.data)
        codename = data['codename']
    except:
        return jsonify({"result": 'Error', "type": 'Subject codename is required'})
    subject = Subject.query.filter_by(codename=codename).first()
    if subject:
        return jsonify(subject_page_funcs.get_tests_info(now_user, subject))
    else:
        return jsonify({"result": 'Error', "type": 'Subject is undefined'})


@user.route('/save_settings', methods=['POST'])
@verification_user
def save_settings(now_user):
    try:
        data = json.loads(request.data)
        name = data['name']
    except:
        return jsonify({"result": 'Error', "type": 'Name is required'})
    now_user.name = name
    db.session.commit()
    return jsonify({"result": 'Success'})


@user.route('/set_general_report', methods=['POST'])
@verification_user
def set_general_report(now_user):
    try:
        data = json.loads(request.data)
        type = data['type']
        page = data['page']
        content = data['content']
        browser = data['browser']
    except:
        return jsonify({"result": 'Error', "type": 'Name, Type, Page, Content are required'})
    report = UserReport(type=type, page=page, content=content, browser=browser, user_id=now_user.id)
    db.session.add(report)
    db.session.commit()
    return jsonify({"result": 'Success'})