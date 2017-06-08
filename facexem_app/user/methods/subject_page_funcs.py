from ...subject.models import Subject, TaskSolve, Task, TestSolve, SessionTasks
from ...achievements.models import Achievement
from ..models import User
import datetime
import time
import json
from ...extensions import db
from ...user.models import SubjectStatic


def update_subject_static(user, subject):
    subject_stat = SubjectStatic.query.filter_by(user_id=user.id, subject_codename=subject.codename).first()
    if subject_stat:
        # update_middle_test_count
        query = db.session.query(Subject, Task, TestSolve).filter(Subject.codename == subject.codename)
        query = query.join(Task)
        query = query.join(TestSolve).filter(TestSolve.user_id == user.id).all()
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
        query = query.join(TaskSolve).filter(TaskSolve.user_id == user.id, TaskSolve.solve == 1)
        query = query.join(SessionTasks).all()
        finish = 0
        for t, ts, st in query:
            now = 0
            for i in st.task_solve_id:
                if i.solve == 1: now += 1
            if now > finish: finish = now
        #update values
        subject_stat.test_points = test_balls
        subject_stat.last_random_task_time = time_tasks
        subject_stat.best_session_list = finish
        subject_stat.date_reload = time.time()
        db.session.commit()


def task_info(user, subject):
    subject_static = SubjectStatic.query.filter_by(user_id=user.id).first()
    if subject_static:
        #10800 = 3 hours
        if time.time()-10800 >= subject_static.date_reload:
            update_subject_static(user, subject)
        subject_stat = SubjectStatic.query.filter_by(user_id=user.id, subject_codename=subject.codename).first()
        if subject_stat:
            table = subject.system_points
            return ({"best_task_random": subject_stat.best_session_list,
                     "mid_time": subject_stat.last_random_task_time,
                     "task_table": table})
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
