from ...subject.models import Subject, TaskSolve, Task, TestSolve, SessionTasks
from ...achievements.models import Achievement
from ..models import User
import datetime
import time
import json
from ...extensions import db
from ...user.models import SubjectStatic


def update_subject_static(user, subject):
    big_time = time.time()
    subject_stat = SubjectStatic.query.filter_by(user_id=user.id, subject_codename=subject.codename).first()
    if subject_stat:
        # update_middle_test_count
        query = db.session.query(Subject, Task, TestSolve).filter(Subject.codename == subject.codename)
        query = query.join(Task)
        query = query.join(TestSolve).filter(TestSolve.user_id == user.id, TestSolve.type == 1).all()
        sum = 0
        count = len(query)
        for i in query:
            sum += i.count
        if count == 0: count = 1
        test_balls = int(sum/count)

        # update_middle_task_time
        query = db.session.query(Subject, Task, TaskSolve).filter(Subject.codename == subject.codename)
        query = query.join(Task)
        query = query.join(TaskSolve).filter(
            TaskSolve.solve == 1,
            TaskSolve.user_id == user.id).all()
        sum = 0
        count = len(query)
        # print(query)
        for i, t, ts in query:
            sum += ts.time
        if count == 0: count = 1
        time_tasks = int(sum/count)

        # best_session_list
        query = db.session.query(Task, TaskSolve, SessionTasks).filter(Task.subject_id == subject.id)
        query = query.join(TaskSolve).filter(TaskSolve.user_id == user.id,
                                             TaskSolve.solve == 1,
                                             TaskSolve.type == 2)
        query = query.join(SessionTasks).all()
        finish = 0
        for t, ts, st in query:
            now = 0
            for i in st.task_solve_id:
                if i.solve == 1: now += 1
            if now > finish: finish = now


        # hardest_number
        query = db.session.query(Subject, Task, TaskSolve).filter(Subject.codename == subject.codename)
        query = query.join(Task)
        query = query.join(TaskSolve).filter(
            TaskSolve.user_id == user.id).all()
        table = json.loads(subject.system_points)
        table_future_task = []
        tasks = []
        for i in range(len(table)):
            table_future_task.append({'num': i+1, 'theme': table[i]['theme'],
                                      'solve': 0, 'unsolve': 0, 'procent': 0,
                                      'color': 'yellow'})
        for s, t, ts in query:
            if ts.solve == 1:
                table_future_task[t.number - 1]['solve'] += 1
            else:
                table_future_task[t.number - 1]['unsolve'] += 1

        for y in table_future_task:
            if y['unsolve'] != 0:
                y['procent'] = round((y['solve']/2) / y['unsolve'], 2)
                if y['procent']>1: y['procent'] = 1
            elif y['solve'] != 0: y['procent'] = 1
            else : y['procent'] = 0
            if y['procent'] < 0.3: y['color'] ='red'
            elif y['procent'] >= 0.7 : y['color'] = 'green'
        # sort
        for f in range(len(table_future_task)):
            for x in range(len(table_future_task)):
                if table_future_task[f]['procent'] < table_future_task[x]['procent']:
                    c = table_future_task[f]
                    table_future_task[f] = table_future_task[x]
                    table_future_task[x] = c
        last = {}
        last_hardest_tasks = json.loads(subject_stat.static_tasks_hardest)
        for i in last_hardest_tasks:
            last[i['num']] = i['procent']

        #update values
        subject_stat.test_points = test_balls
        subject_stat.last_random_task_time = time_tasks
        subject_stat.best_session_list = finish
        subject_stat.date_reload = time.time()
        subject_stat.last_tasks_hardest = json.dumps(last)
        subject_stat.static_tasks_hardest = json.dumps(table_future_task)
        subject_stat.time_for_update = round(time.time()-big_time, 4)
        db.session.commit()


def task_info(user, subject):
    subject_static = SubjectStatic.query.filter_by(user_id=user.id).first()
    if subject_static:
        #10800 = 3 hours
        if time.time()-360 >= subject_static.date_reload:
            update_subject_static(user, subject)
        subject_stat = SubjectStatic.query.filter_by(user_id=user.id, subject_codename=subject.codename).first()
        if subject_stat:
            return ({"best_task_random": subject_stat.best_session_list,
                     "test_points": subject_stat.test_points,
                     "mid_time": subject_stat.last_random_task_time,
                     "task_table": json.loads(subject_stat.static_tasks_hardest),
                     "last_task_procents": json.loads(subject_stat.last_tasks_hardest)})
    return {"best_task_random": 0, "mid_time": 0}


def get_subject_activity(user, subject):
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
        # get count tasks on every day
        for i in range(7):
            if i < 6:
                query = db.session.query(Subject, Task, TaskSolve).filter(Subject.codename == subject.codename)
                query = query.join(Task)
                query = query.join(TaskSolve).filter(
                    TaskSolve.alltime >= unix_time[i],
                    TaskSolve.alltime <= unix_time[i + 1],
                    TaskSolve.solve == 1,
                    TaskSolve.user_id == user.id).all()
            else:
                query = db.session.query(Subject, Task, TaskSolve).filter(Subject.codename == subject.codename)
                query = query.join(Task)
                query = query.join(TaskSolve).filter(
                    TaskSolve.alltime >= unix_time[i],
                    TaskSolve.solve == 1,
                    TaskSolve.user_id == user.id).all()
            finals_querys.append(query)
        for i in finals_querys:
            final.append(len(i))
        k = 0
        # processing date to name of month and day of them
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
