import json


def delete_user(smth):
    data = smth.app.post('/api/user/get_token', follow_redirects=False)
    token = json.loads(data.data)
    data = json.dumps({'token': token['result']})
    finish = smth.app.post('/api/user/delete', data=data, follow_redirects=False)
    return finish
