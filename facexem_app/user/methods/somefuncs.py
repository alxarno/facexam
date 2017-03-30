from ...achievements.models import Achievement
from ..models import UserActivity
from ...extensions import db
import json
import datetime
import time


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
