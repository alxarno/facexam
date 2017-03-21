from ..achievements.models import Achievement
from ..extensions import db
import json


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
        try:
            now_achiev = user_achievs[str(ach.id)]
            now_achiev['now'] += 1
        except:
            user_achievs[str(ach.id)] = {'now': 1, 'max': ach.max}
    user.info_page[0].user_achievements = json.dumps(user_achievs)
    db.session.commit()
    return True
