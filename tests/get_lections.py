import json


def get_lections(smth, codename):
    data = smth.app.post('/api/user/get_token', follow_redirects=False)
    token = json.loads(data.data)
    data = json.dumps({'subject_code_name': codename, 'token': token['result']})
    data = smth.app.post('/api/user/get_lections', data=data, follow_redirects=False)
    data = json.loads(data.data)
    if type(data) is list:
        return "Success"
    else:
        return "Error"
