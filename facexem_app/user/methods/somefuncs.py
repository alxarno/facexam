from ...achievements.models import Achievement
from ...subject.models import Subject, Challenge
from ..models import UserActivity
from ...extensions import db
import json
import datetime
import time
from ...admin.models import AppStatic


def reg_achievements_progress(type, user):
    user_achievs = json.loads(user.info_page[0].user_achievements)
    if user_achievs == '':
        user_achievs = {}
    if type == "lection":
        achievements = Achievement.query.filter_by(type="lection").all()
    elif type == "task":
        achievements = Achievement.query.filter_by(type="task").all()
    elif type == "test":
        achievements = Achievement.query.filter_by(type="test").all()
    else:
        return False
    for ach in achievements:
        # user's achievements have {'id':{now, max}} structs
        try:
            now_achiev = user_achievs[str(ach.id)]
            now_achiev['now'] += 1
        except:
            user_achievs[str(ach.id)] = {'now': 1, 'max': ach.max}
    user.info_page[0].user_achievements = json.dumps(user_achievs)
    db.session.commit()
    return True


def set_activity_user(user_activities, now_user, type):
    now_time = time.localtime()
    real_activ = ''
    for activ in user_activities:
        # if some user's activity day is today, that we're working with it
        if activ.date == datetime.date(now_time.tm_year, now_time.tm_mon, now_time.tm_mday):
            real_activ = activ
    # if nothing in user's day is today , we're create today
    if real_activ == '':
        real_activ = UserActivity(date=datetime.date(now_time.tm_year,
                                  now_time.tm_mon, now_time.tm_mday),
                                  lections=0, user=now_user, tasks=0)
        db.session.add(real_activ)
        db.session.commit()
    if type == 'task':
        real_activ.tasks += 1
    return True


def get_random(array, condition):
    final = 0
    for i in range(0, len(array)-1):
        if int(array[i].level_hard) == condition:
            return i
    return final


def add_challenge(now_user, subject):
    real_subject = Subject.query.filter_by(codename=subject.subject_codename).first()
    if real_subject:
        challenges = Challenge.query.filter_by(subject_id=real_subject.id).all()
        try:
            user_level = round(int(subject.points_of_tests)/33)
        except:
            user_level = 0
        user_challenge = challenges[get_random(challenges, user_level)]
        subject.now_challenge = [user_challenge.id, 0, 0]
        db.session.commit()
        return [user_challenge.id, 0, 0]
    else:
        return False


def set_performance(type, p_time):
    statistic = AppStatic.query.first()
    if type == 'get_test':
        performance = json.loads(statistic.performance_test)
    elif type == 'get_task':
        performance = json.loads(statistic.performance_task)
    elif type == 'mypage':
        performance = json.loads(statistic.performance_mypage)
    elif type == 'subject':
        performance = json.loads(statistic.performance_subject)
    else:
        return False
    today = datetime.datetime.today()
    today = datetime.date(today.year, today.month, today.day).strftime("%d.%m.%y")
    n_time = round(time.time() - p_time, 4)
    if performance.get(today):
        performance[today]['time'] += n_time
        performance[today]['count'] += 1
    else:
        performance[today] = {'time': n_time, 'count': 1}
    if type == 'get_test':
        statistic.performance_test = json.dumps(performance)
    elif type == 'get_task':
        statistic.performance_task = json.dumps(performance)
    elif type == 'mypage':
        statistic.performance_mypage = json.dumps(performance)
    elif type == 'subject':
        statistic.performance_subject = json.dumps(performance)
    db.session.commit()
    return True
