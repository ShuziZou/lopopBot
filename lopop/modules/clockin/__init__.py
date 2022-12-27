import json
import time
from copy import deepcopy

from os.path import dirname, join, exists

import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission

#
# from .dao import retryHealth
#
# sv_help = '''
# [自动打卡绑定 学号 密码]
# [自动打卡解绑 学号]
# [今天我做了核酸] 自动更新核酸日期并打卡
# [今日打卡] 手动打卡 (每日早8点自动执行一次）
# '''.strip()
#
curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'account_bind': {}
}
if exists(config):
    with open(config) as fp:
        root = json.load(fp)

binds = root['account_bind']


# @on_command('帮助')
# async def send_clockin_help(sess: CommandSession):
#     await sess.send(f'{sv_help}')
#
#
# @on_command('查询打卡绑定', permission=permission.SUPERUSER)
# async def query_binds(sess: CommandSession):
#     await sess.send(str(len(binds)))
#
#
@on_command('群发消息', aliases={'公告'}, permission=permission.SUPERUSER)
async def send_msg(sess: CommandSession):
    global binds
    content = sess.current_arg.strip()
    bot = nonebot.get_bot()
    bind_cache = deepcopy(binds)
    for qq in bind_cache:
        await bot.send_private_msg(user_id=int(qq), message=content)
        time.sleep(5)
#
#
# @on_command('今日打卡')
# async def clockin_main(sess: CommandSession):
#     qq = str(sess.ctx['user_id'])
#     if not qq in binds:
#         await sess.send('QQ号未绑定')
#         return
#     info = binds[qq]
#     ans = retryHealth(info['username'], info['password'], False)
#     await sess.send(str(ans))
#
#
# @on_command('自动打卡绑定')
# async def on_clockin_bind(sess: CommandSession):
#     global binds
#     content = sess.current_arg.strip()
#     content = content.split()
#     qq = str(sess.ctx["sender"]["user_id"])
#     account = content[0]
#     password = content[1]
#     binds[qq] = {
#         'username': account,
#         'password': password,
#     }
#     save_binds()
#     await sess.send(message=f'自动打卡绑定成功')
#
#
# @on_command('自动打卡解绑')
# async def delete_account_sub(sess: CommandSession):
#     global binds
#     qq = str(sess.ctx['user_id'])
#     if not qq in binds:
#         await sess.send('未绑定')
#         return
#     delete_account(qq)
#     await sess.send('删除绑定成功')
#
#
# @on_command('今天我做了核酸')
# async def nucleic_acid_clockin(sess: CommandSession):
#     global binds
#     qq = str(sess.ctx['user_id'])
#     nucleic_acid = time.strftime("%Y-%m-%d", time.localtime())
#     if not qq in binds:
#         await sess.send('QQ号未绑定')
#         return
#     info = binds[qq]
#     ans = retryHealth(info['username'], info['password'], nocheck=False, nucleic_acid=nucleic_acid)
#     await sess.send(str(ans))
#
#
# @nonebot.scheduler.scheduled_job('cron', hour='8', jitter=300)
# async def on_clockin_schedule():
#     bot = nonebot.get_bot()
#     bind_cache = deepcopy(binds)
#     for qq in bind_cache:
#         info = bind_cache[qq]
#         try:
#             print(f'为{info["username"]} 打卡中')
#             ans = retryHealth(info['username'], info['password'], False)
#             await bot.send_private_msg(user_id=qq, message=ans)
#             time.sleep(3)
#         except Exception:
#             pass
#
#
# # 自动通过好友请求
# @on_request()
# async def on_friend_approve(sess: RequestSession):
#     print(sess.event)
#     await sess.approve()
#
#
# def delete_account(qq):
#     binds.pop(qq)
#     save_binds()
#
#
# def save_binds():
#     with open(config, 'w') as fp:
#         json.dump(root, fp, indent=4)
