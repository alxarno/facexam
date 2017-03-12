import json


def get_page_info(smth, photo='', about='', achivs=None, background=''):
    data = smth.app.post('/api/user/get_token', follow_redirects=False)
    token = json.loads(data.data)
    data = json.dumps({'token': token['result']})
    finish = smth.app.post('/api/user/get_page_info', data=data, follow_redirects=False)
    finish = json.loads(finish.data)
    finish = finish[0]
    if finish['photo'] == photo:
        return "Success"
    else:
        return "Error"
