import json
from os.path import *

from nonebot import on_command, permission, CommandSession

curpath = dirname(__file__)
config = join(curpath, 'binds.json')
binds = {}

if exists(config):
    with open(config, 'r', encoding='utf-8') as f:
        binds = json.load(f)

sv_help = '''
[存储信息,cc] 键 值
[查询信息,cx] 键
[查询键,cxkey]
[清空spm数据]
'''.strip()


@on_command('信息帮助')
async def help(sess: CommandSession):
    await sess.finish(message=sv_help)


@on_command('查询键', aliases={'cxkey'}, permission=permission.SUPERUSER)
async def queryKeys(se: CommandSession):
    msg = binds.keys()
    await se.finish(message=str(msg))


@on_command('存储信息', aliases={'cc'}, permission=permission.SUPERUSER)
async def saveMessage(sess: CommandSession):
    global binds
    msg = sess.current_arg_text.strip()
    if not msg:
        msg = (await sess.aget(prompt='请输入键值对')).strip()
        while not msg:
            msg = (await sess.aget(prompt='请输入键值对')).strip()
    msg = msg.split()

    key = msg[0]
    raw_value = []
    if key in binds:
        raw_value = binds[key]
        await sess.send(message='注意，键已存在，将要把值追加到末尾')

    if len(msg) == 1:
        value = (await sess.aget(prompt='请输入需要保存的值：'))
        while not value:
            value = (await sess.aget(prompt='请输入需要保存的值：'))
    else:
        value = msg[1]

    if key == '结束' or value == '结束':
        await sess.finish(message='会话结束。')
    else:
        raw_value.append(value)
        binds[key] = raw_value
        saveBinds()
        await sess.finish(message='插入成功。')


@on_command('查询信息', aliases={'cx', 'query'}, permission=permission.SUPERUSER)
async def queryBinds(session: CommandSession):
    key = session.current_arg_text.strip()
    if key == '结束':
        await session.finish(message='查询终止。')
        return
    if key not in binds:
        key = (await session.aget(prompt='键不存在，请重新输入：'))
        if key == '结束':
            await session.finish(message='查询终止。')
            return
        while key not in binds:
            key = (await session.aget(prompt='键不存在，请重新输入：'))
            if key == '结束':
                await session.finish(message='查询终止。')
                return
    msg = str(binds[key])
    await session.send(message=msg)


@on_command('清空spm数据', permission=permission.SUPERUSER)
async def clearBinds(sess: CommandSession):
    binds.clear()
    saveBinds()
    await sess.finish(message='清空成功')


def saveBinds():
    with open(config, 'w', encoding='utf-8') as f:
        json.dump(binds, f, indent=4)
