from ...subject.models import Subject, TaskSolve, TestSolve, Task, Content, TestTask
import datetime
import time
import json
from ...extensions import db



def get_user_task(user, subject, number, count):
    #First we get all user's tasks solve that know what tasks he already solved
    query = db.session.query(Subject, Task, TaskSolve, Content).filter(Subject.codename == subject.codename)
    query = query.join(Task).filter(Task.number == number, Task.open == 1)
    query = query.join(TaskSolve).filter(TaskSolve.solve == 1, TaskSolve.user_id == user.id)
    query = query.order_by(TaskSolve.alltime.asc())
    query = query.join(Content).limit(5).all()
    task_solved_id = []
    solved_tasks = []
    for s, t, ts, c in query:
        task_solved_id.append(ts.task_id)
        solved_tasks.append([s, t, c])
    # print(solved_tasks)
    user_future_task = db.session.query(Subject, Task, Content).filter(Subject.codename == subject.codename)
    user_future_task = user_future_task.join(Task).filter(Task.number == number, Task.open == 1, ~Task.id.in_(task_solved_id))
    user_future_task = user_future_task.join(Content).limit(count).all()
    if len(user_future_task) < count:
        for i in range(count-len(user_future_task)):
            if len(solved_tasks) > i:
                try:
                    user_future_task.append(solved_tasks[i])
                except:
                    None
    final = []
    for s, t, c in user_future_task:
        content = json.loads(c.content)
        final.append({
            "id": t.id,
            "number": t.number,
            "content": content
        })

    return final


def check_test(user, answers, subject, u_time, type):
    ids = list(answers.keys())
    table = json.loads(subject.system_points)
    counts = []
    query = db.session.query(Task, Content).filter(Task.id.in_(ids))
    query = query.join(Content).all()
    test = TestSolve(time=u_time, count=0, type=type, solve=0, subject_id=subject.id, date=time.time(), user_id=user.id)
    db.session.add(test)
    db.session.commit()
    all_count = 0
    need_count = 0
    for t, c in query:
        count = 0
        user_answer = answers[str(t.id)]
        real_answer = json.loads(c.answers)
        print(user_answer)
        print(real_answer)
        for i in range(len(real_answer)):
            try:
                if user_answer[i] == real_answer[i]:
                    count += 1
            except:
                None
        all_count += count
        need_count += len(real_answer)
        solve = 0
        if count != 0:
            solve = 1
        task = TestTask(solve=solve, count=count, task_id=t.id, test_id=test.id, answer=json.dumps(user_answer))
        db.session.add(task)
        db.session.commit()
        # counts.append({
        #     "u_points": count,
        #     "need": table[t.number-1]['count'],
        #     "description": json.loads(c.description),
        #     "content": json.loads(c.content),
        #     "u_answer": user_answer
        # })
    solve = 0
    limit = subject.min_point_test/100
    if all_count >= need_count*limit and u_time < subject.time_pass:
        solve = 1
    test = TestSolve.query.filter_by(id=test.id).first()
    test.count = all_count
    test.need_count = need_count
    test.solve = solve
    test.hundred_value = round(5.7271*all_count**0.8824, 1)
    test.hundred_need_count = round(5.7271*need_count**0.8824, 1)
    db.session.commit()
    return test.id


def get_test_results(user, test, subject):
    final = {'main': {
        "count": test.count,
        "need_count": test.need_count,
        "time": test.time,
        "need_time": subject.time_pass,
        "solve": test.solve,
        "hundred_value": test.hundred_value,
        "need_hundred_value": test.hundred_need_count
    }}
    table = json.loads(subject.system_points)
    points = {}
    for i in range(len(table)):
        points[str(i+1)] = table[i]['count']
    contents = []
    query = db.session.query(TestTask, Task, Content).filter(TestTask.test_id == test.id)
    query = query.join(Task)
    query = query.join(Content)
    for tt, t, c in query:
        contents.append({
            "number": t.number,
            "id": t.id,
            "task": json.loads(c.content),
            "description": json.loads(c.description),
            "answer": json.loads(c.answers),
            "u_answer": json.loads(tt.answer),
            "count": tt.count,
            "need_count": points[str(t.number)],
            "solve": tt.solve,
        })
    final['detail'] = contents
    return final