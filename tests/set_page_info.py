import json


def set_page_info(smth, photo='', about='', achivs=None, background=''):
    if achivs is None:
        achivs = []
    data = smth.app.post('/api/user/get_token', follow_redirects=False)
    token = json.loads(data.data)
    data = json.dumps({'token': token['result'], 'photo': photo, 'about': about,
                       'achivs': json.dumps(achivs), 'background': background})
    finish = smth.app.post('/api/user/set_page_info', data=data, follow_redirects=False)
    return finish
