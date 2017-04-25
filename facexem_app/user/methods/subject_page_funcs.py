from ...subject.models import Subject
from ...achievements.models import Achievement
from ..models import User
import datetime
import time
import json



def get_subject_activity(user, subject_codename):
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

    user_activities = user.info_subjects
    real_activity = 0
    for i in user_activities:
        if subject_codename == i.subject_codename:
            real_activity = i.activity
    if real_activity == 0:
        return False
    try:
        real_activity = json.loads(real_activity)
    except:
        return False
    for d in dates:
        if d in real_activity:
            final.append(real_activity[d])
        else:
            final.append(0)

    k = 0
    for date in dates:
        dayDate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        day = str(dayDate.strftime("%d"))
        month = int(dayDate.strftime("%m"))
        months = ['Января', 'Февраля', "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа",
                  "Сентября", "Ноября", "Декабря"]
        month = months[month - 1]
        date = str(day + " " + month)
        dates[k] = date
        k += 1
    return [final, dates]