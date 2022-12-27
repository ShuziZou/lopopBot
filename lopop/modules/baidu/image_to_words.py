# encoding:utf-8
import json

import requests
import base64

'''
通用文字识别
'''


def get_token():
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=rlEgGjIyiAc0HOT09xP1juKX&client_secret=MMCy4YrfzWIikxV4Dr4LmHouc7lqM8K0'
    res = requests.post(url=url)
    if res:
        # print(res.json())
        token = res.json()['access_token']
        return token


def do_i2w(url: str):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token="
    params = {"url": url}
    access_token = '24.9a72bfd8d0b89242952264ce0aec704e.2592000.1674045783.282335-29165047'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    for i in range(2):
        try:
            response = requests.post(request_url + access_token, data=params, headers=headers).json()
            return response['words_result']
        except:
            print('access_token已过期，尝试重新获取')
            access_token = get_token()
