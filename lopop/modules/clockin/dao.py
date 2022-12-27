# 自动健康打卡，取上次上传数据作为本次打卡数据
import json
import time
import traceback

import ddddocr
import requests
from bs4 import BeautifulSoup


def sendMessage(msg):
    # print(msg)
    return msg
    # 如果需要通知提醒，请在此处添加邮箱、或QQ机器人、微信企业号、微信公众号、pushplus等通知提醒功能的代码


def getCaptcha(session):
    url = 'https://u.njtech.edu.cn/cas/captcha.jpg'
    img = session.get(url)
    ocr = ddddocr.DdddOcr(show_ad=False)
    res = ocr.classification(img.content)
    return res


# 如果第三个参数填True，会将健康码行程码填为不存在的图片，一样可以成功打卡，永远不会提示过期。（此举有风险，造成任何后果本人概不负责）
def healthFill(username, password, nocheck, nucleic_acid=None):
    loginUrl = 'https://u.njtech.edu.cn/cas/login?service=http://pdc.njtech.edu.cn/#/dform/genericForm/wbfjIwyK'
    session = requests.Session()
    # 通过i南工进行登录，获取i南工登录页面
    response = session.get(loginUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    lt0 = soup.find('input', attrs={'name': 'lt'})['value']
    execution0 = soup.find('input', attrs={'name': 'execution'})['value']
    loginPostUrl = 'https://u.njtech.edu.cn' + \
                   soup.select("#fm2")[0].attrs['action']

    captcha = getCaptcha(session)

    loginPostData = {
        'username': username,
        'password': password,
        'channelshow': '校园内网',
        'channel': 'default',
        'lt': lt0,
        'captcha': captcha,
        'execution': execution0,
        '_eventId': 'submit',
        'login': '登录',
    }

    # 登录并获取登录后的cookie
    response = session.post(loginPostUrl, data=loginPostData, allow_redirects=False)
    loginRedirectUrl = response.headers.get('Location')
    try:
        ticket = loginRedirectUrl.split('?ticket=')[-1].split('#/')[0]
    except Exception:
        return sendMessage("登录失败？请检查账号密码是否正确"), False
    pageHeaders = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 5.0.2; zh-cn; MI 2C Build/LRX22G) AppleWebKit/533.1 (KHTML, like Gecko)Version/4.0 MQQBrowser/5.4 TBS/025469 Mobile Safari/533.1 MicroMessenger/6.2.5.53_r2565f18.621 NetType/WIFI Language/zh_CN",
    }
    pageHeaders["Referer"] = "http://pdc.njtech.edu.cn/?ticket={}".format(ticket)

    # 获取表单内容（好像用不到）
    # response = session.get(loginRedirectUrl, headers=pageHeaders, allow_redirects=False)

    try:
        # 获取token
        response = session.get(
            "http://pdc.njtech.edu.cn/dfi/validateLogin?ticket={}&service=http://pdc.njtech.edu.cn/#/dform/genericForm/wbfjIwyK".format(
                ticket), headers=pageHeaders, allow_redirects=False)
        token = json.loads(response.content)['data']['token']
        pageHeaders["Authentication"] = token
        # 到此处，登录已完成

        # 获取wid
        response = session.get("http://pdc.njtech.edu.cn/dfi/formOpen/loadFormListBySUrl?sUrl=wbfjIwyK",
                               headers=pageHeaders, allow_redirects=False)
        wid = json.loads(response.content)['data'][0]['WID']

        # 获取历史提交记录
        response = session.get(
            "http://pdc.njtech.edu.cn/dfi/formData/loadFormFillHistoryDataList?formWid={}&auditConfigWid=".format(
                wid), headers=pageHeaders, allow_redirects=False)
        # 取最近一次提交数据，数据的结构和提交所需的结构不完全一致，进行修改后作为此次提交数据
        # lastData = json.loads(response.content)["data"]
        # print(lastData)
        historyData = json.loads(response.content)["data"]
        # 默认值设为不存在的图片
        healthCode = ['null.jpg']
        tourCode = ['none.jpg']

        # 如果设置了不检查健康码、行程码则跳过此步
        if not nocheck:
            # 判断健康码、行程码是否过期
            tryTimes = 0
            while tryTimes < 2: # 向前找两个
                try:
                    lastData = historyData[tryTimes]
                    healthCode = lastData['ONEIMAGEUPLOAD_KWYTQFT3'][1:-1].split(', ')
                    tourCode = lastData['ONEIMAGEUPLOAD_KWYTQFT5'][1:-1].split(', ')
                    break
                except Exception:
                    tryTimes += 1
            if tryTimes >= 3:
                return sendMessage("❗❗❗健康打卡提交失败！\n健康码或身份码过期")
        dataMap = {
            "wid": "",
            "RADIO_KWYTQFSU": "本人知情承诺",  # 知情承诺
            "INPUT_KWYTQFSO": lastData['INPUT_KWYTQFSO'],  # 学号
            "INPUT_KWYTQFSP": lastData['INPUT_KWYTQFSP'],  # 姓名
            "SELECT_KX3ZXSAE": lastData['SELECT_KX3ZXSAE'],  # 学院
            "INPUT_KWYTQFSS": lastData['INPUT_KWYTQFSS'],  # 班级
            "INPUT_KX3ZXSAD": lastData['INPUT_KX3ZXSAD'],  # 手机号
            "INPUT_KWYUM2SI": lastData['INPUT_KWYUM2SI'],  # 辅导员
            "RADIO_KWYTQFSZ": lastData['RADIO_KWYTQFSZ'],  # 当前位置
            "RADIO_KWYTQFT0": lastData['RADIO_KWYTQFT0'],
            "DATEPICKER_L8Z744C5": lastData["DATEPICKER_L8Z744C5"] if not nucleic_acid else nucleic_acid,  # 新增了一个核酸检测日期
            "CASCADER_KWYTQFT1": lastData['CASCADER_KWYTQFT1'][1:-1].split(', '),  # 所在省市区
            "RADIO_KWYTQFT2": lastData['RADIO_KWYTQFT2'],  # 身体状况
            # 下面这两行如果报出现异常一般是健康码行程码过期（一般两周左右会过期一次），需要自己重新打卡一次
            "ONEIMAGEUPLOAD_KWYTQFT3": healthCode,  # 健康码
            "ONEIMAGEUPLOAD_KWYTQFT5": tourCode,  # 行程码
            "LOCATION_KWYTQFT7": lastData['LOCATION_KWYTQFT7'],  # 定位
        }

        # 构建AMID（不知道有啥意义，可能用于迷惑人，就是个时间戳，前面可能会加一个随机数，但是不加也可以）
        AMID = "AM@" + str(int(time.time() * 1000))

        # 获取微信api数据（好像用不到）
        # response = session.get("http://pdc.njtech.edu.cn/dfi/weChatApi/loadWeChatJsSdk?formUrl=http://pdc.njtech.edu.cn/",headers=pageHeaders,allow_redirects=False)

        # 数据校验（好像用不到）
        # postData=json.dumps({
        #     "dataMap": {},
        #     "formWid": wid,
        #     "userId": AMID,
        # })
        # response = session.post('http://pdc.njtech.edu.cn/dfi/formOpen/checkFormFieldIsRisk',data=postData,headers=pageHeaders,allow_redirects=False)

        # 发送表单数据
        postData = json.dumps({
            "auditConfigWid": "",
            "commitDate": time.strftime("%Y-%m-%d", time.localtime()),
            "commitMonth": time.strftime("%Y-%m", time.localtime()),
            "dataMap": dataMap,
            "formWid": wid,
            "userId": AMID,
        })
        response = session.post('http://pdc.njtech.edu.cn/dfi/formData/saveFormSubmitData',
                                data=postData.encode("utf-8"), headers=pageHeaders, allow_redirects=False)
        if json.loads(response.content)["message"] == "请求成功":
            response = session.get(
                "http://pdc.njtech.edu.cn/dfi/formData/loadFormFillHistoryDataList?formWid={}&auditConfigWid=".format(
                    wid), headers=pageHeaders, allow_redirects=False)
            response = json.loads(response.content)["data"][0]
            result = {
                '学号': response['INPUT_KWYTQFSO'],
                '姓名': response['INPUT_KWYTQFSP'],
                '学院': response['SELECT_KX3ZXSAE'],
                '班级': response['INPUT_KWYTQFSS'],
                '当前位置': response['RADIO_KWYTQFSZ'],
                '所在省市区': response['CASCADER_KWYTQFT1'],
                '定位': response['LOCATION_KWYTQFT7'],
                '身体状况': response['RADIO_KWYTQFT2'],
                '最新核酸检测时间': response['DATEPICKER_L8Z744C5']
            }
            return sendMessage("健康打卡提交成功！\n此次提交的数据内容如下：\n" + json.dumps(result,
                                                                                           indent=0,
                                                                                           separators=(', ', ': '),
                                                                                           ensure_ascii=False)[
                                                                                2:-1]), True
        else:
            return sendMessage("❗❗❗健康打卡提交失败！\n数据提交失败，服务器未响应")
    except Exception as e:
        return sendMessage("❗❗❗健康打卡提交失败！\n报错信息如下：\n" + traceback.format_exc())


# 自动重试
def retryHealth(username, password, nocheck, maxRetryTimes=3, nucleic_acid=None):
    ans = ''
    for i in range(maxRetryTimes):
        ans = healthFill(username, password, nocheck, nucleic_acid=nucleic_acid)
        if isinstance(ans, tuple):
            return ans[0]
    return ans
