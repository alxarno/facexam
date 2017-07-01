from ...subject.models import Subject, TaskSolve, TestSolve, Task, SessionTasks
from ...achievements.models import Achievement
from ...author.models import Author
import datetime
import time
import json
from ...extensions import db




def user_get_subjects(user):
    subjects = user.subjects_statics
    result = []
    for s in subjects:
        real_subject = Subject.query.filter_by(codename=s.subject_codename).first()
        if real_subject:
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

    #CHANGE!!!!
    # if user.role == 3:
    roots = 'user'
    current_author = Author.query.filter_by(user_id=user.id).first()
    if current_author:
        roots = 'author'
    # elif user == 2:
    # roots = 'author'
    # else:
    # roots = 'user'
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
    unix_time = []
    i = 6
    while i >= 0:
        date = now_date - datetime.timedelta(days=i)
        dates.append(str(date))
        unix_time.append(time.mktime(date.timetuple()))
        i -= 1
    finals_querys = []
    for i in range(7):
        if i < 6:
            query = db.session.query(TaskSolve).filter(
                TaskSolve.alltime >= unix_time[i],
                TaskSolve.alltime <= unix_time[i+1],
                TaskSolve.solve == 1,
                TaskSolve.user_id == user.id).all()
        else:
            query = db.session.query(TaskSolve).filter(
                TaskSolve.alltime >= unix_time[i],
                TaskSolve.solve == 1,
                TaskSolve.user_id == user.id).all()
        finals_querys.append(query)

    for i in finals_querys:
        final.append(len(i))
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
    return {'values': final, 'dates': dates}


def user_get_preference(user):
    names = []
    values = []
    user_subjects = user.subjects_statics
    for sub in user_subjects:
        subject = Subject.query.filter_by(codename=sub.subject_codename).first()
        names.append(subject.name)
        # try:
        # tasks = db.session.query(TaskSolve).filter(TaskSolve.user_id == user.id)
        # tasks = tasks.join(Task, Task.subject_id == subject.id)
        # tasks = tasks.all()
        tasks = db.session.query(Subject, Task, TaskSolve).filter(Subject.codename == sub.subject_codename)
        tasks = tasks.join(Task)
        tasks = tasks.join(TaskSolve).filter(
            TaskSolve.user_id == user.id).all()
        values.append(len(tasks))
    return [values, names]


def user_get_last_actions(user):
    query_task = db.session.query(SessionTasks).order_by(SessionTasks.date.desc()).limit(7).all()
    some_query = db.session.query(TestSolve).order_by(TestSolve.alltime.desc()).limit(7).all()
    all=[]
    for i in query_task:
        try:
            i.alltime = i.date
        except:
            None
        all.append({'type': 'few_tasks', "content": i})
    for i in some_query:
        all.append({'type': 'test', "content": i})
    for i in range(len(all)):
        for y in range(len(all)):
            if i != y:
                if all[i]['content'].alltime > all[y]['content'].alltime:
                    c = all[i]
                    all[i] = all[y]
                    all[y] = c

    final = []
    for i in all[:6]:
        if i['type'] == 'few_tasks':
            subject = db.session.query(Subject).filter_by(id=i['content'].subject_id).first()
            # tasks = db.session.query(Task, Subject).filter(Task.id == i['content'].task_id)
            if subject:
                tasks = db.session.query(SessionTasks, TaskSolve).filter(
                    SessionTasks.id == i['content'].id
                ).join(TaskSolve).filter(TaskSolve.solve == 1).count()
                word = 'заданий'
                if tasks > 0:
                    if tasks == 1:
                       word = 'задание'
                    elif tasks < 5:
                        word = 'задания'
                    final.append({
                        "text": str(tasks) + " " + word + " решенно по предмету " + subject.name,
                        "img": "/icon/test-tube"
                    })
        else:
            subject = db.session.query(Subject).filter_by(id=i['content'].subject_id).first()
            if subject:
                word = 'Не решен'
                img = '/icon/flask_1'
                if i['content'].solve == 1:
                    word = 'Решен'
                    img = "/icon/flask"
                try:
                    final.append({
                        "text": word + " тест по предмету " + subject.name + " на "
                                + str(round(i['content'].hundred_value)) + " баллов из "
                                + str(round(i['content'].hundred_need_count)),
                        "img": img,
                        "link": "/"+subject.codename + "/mytest/" + str(i['content'].id)
                    })
                except:
                    None
    return final


def user_get_global_static(user):
    subjects = user.subjects_statics
    middle = 0
    tasks = 0
    test = 0
    if subjects:
        tasks += TaskSolve.query.filter_by(solve=1).count()
        test += TestSolve.query.filter_by(solve=1).count()
        for i in subjects:
            middle += i.test_points
            tasks += i.solve_delete_tasks
        result = {'middle': middle,
                  'tasks': tasks,
                  'tests': test}
        return result
    else:
        return 0


