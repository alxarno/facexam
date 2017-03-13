import json


def set_subject(smth, codenames=None):
    if codenames is None:
        codenames = []
    data = smth.app.post('/api/user/get_token', follow_redirects=False)
    token = json.loads(data.data)
    data = json.dumps({'token': token['result'], 'codenames': codenames})
    answer = smth.app.post('/api/user/set_subjects', data=data, follow_redirects=False)
    return answer
