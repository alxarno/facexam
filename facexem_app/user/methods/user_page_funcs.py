from ...subject.models import Subject
from ...achievements.models import Achievement
from ..models import User
import datetime
import time
import json




def user_get_subjects(user):
    subjects = user.info_subjects
    result = []
    for s in subjects:
        real_subject = Subject.query.filter_by(codename=s.subject_codename).first()
        if real_subject:
            subject_count = s.points_of_tests
            if subject_count == '':
                subject_count = 0
            subject = {'link': s.subject_codename,
                       'subjectName': real_subject.name,
                       'image': 'subject_pic/' + s.subject_codename,
                       'subjectCount': subject_count,
                       'subjectAll': 100}
            result.append(subject)
    return result


def user_get_page_info(user):
    info = user.info_page
    name = user.name
    city = info[0].city
    exp = info[0].experience
    badges = info[0].user_active_achivs
    photo = info[0].photo
    about = info[0].about
    background = info[0].user_active_background
    final_achiev = []
    if badges:
        try:
            badges = json.loads(badges)
            for b in badges:
                achiev = Achievement.query.filter_by(id=b).first()
                if achiev:
                    url = 'achiev/'+str(achiev.id)
                    achiev = {'img': url, 'tooltip': achiev.name}
                    final_achiev.append(achiev)
        except:
            final_achiev = []
    if user.role == 3:
        roots = 'admin'
    elif user == 2:
        roots = 'author'
    else:
        roots = 'user'
    finish = [{'photo': photo,
               'about': about,
               'background': background,
               'badges': final_achiev,
               'name': name,
               'city': city,
               'exp': exp,
               'roots': roots,
               'streack': 5}]
    return finish


def user_get_activity(user):
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

    user_activities = user.activity
    # test, is day of activity in last 7 days
    for day in user_activities:
        if str(day.date) in dates:
            print(day.date)
            final.append(day.lections)
    if len(final) < 7:
        times = len(final)
        while times < 7:
            final.append(0)
            times += 1
    final = list(reversed(final))
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


def user_get_preference(user):
    names = []
    values = []
    user_subjects = user.info_subjects
    for sub in user_subjects:
        subject = Subject.query.filter_by(codename=sub.subject_codename).first()
        names.append(subject.name)
        try:
            values.append(int(sub.tasks) * (int(sub.points_of_tests) / 100))
        except:
            values.append(0)
    return [values, names]


def user_get_last_actions(user):
    final = []
    actions = user.info_page[0].last_actions
    if not actions:
        actions = []
    for action in json.loads(actions):
        subject = Subject.query.filter_by(id=action['subject']).first()
        if action['type'] == "tasks":
            final.append({"text": str(action['count']) + " заданий по предмету " + subject.name,
                          "img": "http://127.0.0.1:9999/icon/test-tube"})
        elif action['type'] == 'test':
            if action['test_type'] == 'usually':
                final.append({"text": "Обычный тест по предмету " + subject.name + \
                                      " с " + str(action['count']) + " баллами из 100",
                              "img": "http://127.0.0.1:9999/icon/flask"})
            elif action['test_type'] == 'custom':
                final.append({"text": "Индивидуальный тест по предмету " + subject.name + \
                                      " с " + str(action['count']) + " первичными баллами",
                              "img": "http://127.0.0.1:9999/icon/flask_1"})
    return final


def user_get_global_static(user):
    info = user.info_page[0]
    subjects = user.info_subjects
    if subjects:
        count = 1
        sum = 0
        for subject in subjects:
            try:
                sum += int(subject.points_of_tests)
            except:
                sum += 0
            count += 1
        middle_point = sum / count
        try:
            tasks = int(info.tasks)
        except:
            tasks = 0
        try:
            tests = int(info.tasks)
        except:
            tests = 0
        result = {'middle': middle_point,
                  'tasks': tasks,
                  'tests': tests}
        return result
    else:
        return 0


def user_get_notifications(user):
    notifics = user.notifications
    result = []
    if notifics:
        for notif in notifics:
            author = User.query.get(notif.author)
            author_photo = author.info_page[0].photo
            notif = {'author': author.name,
                     'authorPhoto': author_photo,
                     'text': notif.text,
                     'type': notif.type}
            result.append(notif)
    return result
