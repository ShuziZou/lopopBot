import json
import re

import requests


def get_token():
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=mW83cpy4G34CqQZiofiG2Sxz&client_secret=qiFG4bKQEjiZ8HdfgtDghyWXLvr6IIuo'
    res = requests.post(url=url)
    if res:
        token = res.json()['access_token']
        return token


def do_translate(q: str):
    q = q.replace('\n', ' ')
    # token = '【调用鉴权接口获取的token】'
    token = '24.95e1d8e8c25afec56c76fee2996df8dd.2592000.1672906261.282335-28871527'
    url = 'https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token='

    # q = 'what are you doing'  # example: hello
    # For list of language codes, please refer to `https://ai.baidu.com/ai-doc/MT/4kqryjku9#语种列表`
    if re.search('[a-zA-Z]', q):
        from_lang = 'en'  # example: en
    else:
        from_lang = 'zh'
    if from_lang == 'en':
        to_lang = 'zh'  # example: zh
    else:
        to_lang = 'en'
    term_ids = ''  # 术语库id，多个逗号隔开

    # Build request
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    payload = {'q': q, 'from': from_lang, 'to': to_lang, 'termIds': term_ids}

    for i in range(2):
        try:
            # Send request
            r = requests.post(url + token, params=payload, headers=headers)
            result = r.json()
            return result['result']['trans_result']
        except:
            print('token过期，尝试重新获取')
            token = get_token()
