import json
import re
from os.path import dirname, join, exists

import nonebot
import requests
from aiocqhttp import MessageSegment
from nonebot import on_command, CommandSession, permission
from nonebot.command.argfilter import extractors

from .getCookie.golib_cookie import golib_getCookie
from .iGrab.reserve_specific_floor import reserveSeat
from .iGrab.cookie_loop import update_cookie

curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'account_bind': {}
}

if exists(config):
    with open(config) as fp:
        root = json.load(fp)

binds = root['account_bind']


def delete_account(qq):
    binds.pop(qq)
    save_binds()


def save_binds():
    with open(config, 'w') as fp:
        json.dump(root, fp, indent=4)


def reload_binds():
    global binds
    with open(config) as fp:
        root = json.load(fp)
    binds = root['account_bind']


@on_command('预约座位')
async def reserve_seat(sess: CommandSession):
    global binds
    qq = str(sess.ctx['user_id'])
    if qq not in binds:
        img = MessageSegment.image(f'''file:///{join(curpath, 'getCookie', 'qr.png')}''')
        msg = f'''1. 使用微信扫描下方二维码
2. 点击微信右上角“…”符号，选择“复制链接”。
3. 将该url发送给机器人{img}'''
        url = await sess.aget(prompt=msg, arg_filters=[
            extractors.extract_text,  # 取纯文本部分
            str.strip  # 去掉两边空白字符
        ])
        cookie = golib_getCookie(url)
        binds[qq] = {'cookie': cookie}
    else:
        cookie = binds[qq]['cookie']
    seatkey = await reserveSeat(sess, cookie)
    if seatkey:
        binds[qq]['seat'] = seatkey


@on_command('删除座位')
async def _(sess: CommandSession):
    qq = str(sess.ctx['user_id'])
    binds.pop(qq)
    save_binds()
    await sess.finish('删除成功')


@on_command('更新cookie', aliases={'updcookie'}, permission=permission.SUPERUSER)
async def _(sess: CommandSession):
    updateBinds()
    await sess.finish('更新成功')


# @nonebot.scheduler.scheduled_job('cron', minute='*/5', jitter=200)
async def _():
    updateBinds()


def updateBinds():
    global binds
    myheaders = {'Host': 'wechat.v2.traceint.com', 'Connection': 'keep-alive', 'Content-Length': '729',
                 'User-Agent': 'Mozilla/5.0 (Linux; Android 11; M2012K11AC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3149 MMWEBSDK/20211001 Mobile '
                               'Safari/537.36 MMWEBID/68 MicroMessenger/8.0.16.2040(0x28001053) Process/toolsmp '
                               'WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
                 'Content-Type': 'application/json', 'Accept': '*/*', 'Origin': 'https://web.traceint.com',
                 'X-Requested-With': 'com.tencent.mm', 'Sec-Fetch-Site': 'same-site', 'Sec-Fetch-Mode': 'cors',
                 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://web.traceint.com/web/index.html',
                 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'}
    check_library_body = {"operationName": "list",
                          "query": "query list {\n userAuth {\n reserve {\n libs(libType: -1) {\n "
                                   "lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n "
                                   "lib_group_id\n lib_comment\n lib_rt {\n seats_total\n "
                                   "seats_used\n seats_booking\n seats_has\n reserve_ttl\n "
                                   "open_time\n open_time_str\n close_time\n close_time_str\n "
                                   "advance_booking\n }\n }\n libGroups {\n id\n group_name\n }\n "
                                   "reserve {\n isRecordUser\n }\n }\n record {\n libs {\n "
                                   "lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n "
                                   "lib_group_id\n lib_comment\n lib_color_name\n lib_rt {\n "
                                   "seats_total\n seats_used\n seats_booking\n seats_has\n "
                                   "reserve_ttl\n open_time\n open_time_str\n close_time\n "
                                   "close_time_str\n advance_booking\n }\n }\n }\n rule {\n "
                                   "signRule\n }\n }\n}"}
    reload_binds()
    for qq in binds:
        info = binds[qq]
        myheaders['Cookie'] = info['cookie']
        s = requests.session()
        s.headers.clear()
        s.headers.update(myheaders)
        r = s.post("https://wechat.v2.traceint.com/index.php/graphql/",
                   json=check_library_body)
        r_cookie = requests.utils.dict_from_cookiejar(r.cookies)
        info['cookie'] = update_cookie(r_cookie, info['cookie'])
    save_binds()
