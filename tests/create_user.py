import json


def create_user(smth, email, name, password):
    data = json.dumps({'email': email})
    giveway = smth.app.post('/api/user/create', data=data, follow_redirects=False)
    key = json.loads(giveway.data)
    data = json.dumps({'email': email, 'name': name, 'key': key['result'], 'pass': password})
    finish = smth.app.post('/api/user/prove_email', data=data, follow_redirects=False)
    return finish
