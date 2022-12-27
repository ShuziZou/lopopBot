from datetime import datetime

import nonebot
from hoshino.typing import CommandSession
from nonebot import on_command, permission

from lopop.config import SUPERUSERS
from .sqliteDao import Practice

__plugin_name__ = 'functionary'
sv_help = r"""定时任务（无法调用）
上传 [type, total_num, error_num, gain, ...comments]
【全部练习】、【查询练习 pid】、【删除练习 pid】
"""

# sv = Service('functionary', use_priv=priv.SU, manage_priv=priv.SU, enable_on_default=True, help_=sv_help)
practiceDao = Practice()


def get_left_days():
    now = datetime.now()
    guokao = datetime(2023, 1, 7)
    # shanghai = datetime(2022, 12, 11)
    # jiangsu = datetime(2022, 12, 17)
    g_left = (guokao - now).days + 1
    # shanghai_left = (shanghai - now).days + 1
    # jiangsu_left = (jiangsu - now).days + 1
    msg = f'''国考：{g_left}天（1-7笔试）'''
    return msg



@on_command("查询公考", permission=permission.SUPERUSER)
async def get_days(sess: CommandSession):
    await sess.finish(message=get_left_days())


@on_command('sc', aliases={'上报', 'sb', 'SB', '上传', '练习', 'lx'})
async def uploadPractice(session: CommandSession):
    global practiceDao
    content = session.current_arg.strip()
    pc = content.split() if content else []
    print(f"=============={pc}==============")
    tips = ['类型', '题目数量', '错题数量']
    ex = ['原因', '备注', '日期']
    promp = f'''请输入练习的{tips[len(pc):]}***可选{ex}'''
    if len(pc) < 3:
        content = (await session.aget(prompt=promp)).strip()
        if content == '退出':
            await session.send('取消上传')
            return
        pc.extend(content.split())
        # 如果用户只发送空白符，则继续询问
        while not content:
            content = (await session.aget(prompt=promp)).strip()
            if content == '退出':
                await session.send('取消上传')
                return
            pc.extend(content.split() if content else None)

    # if not isinstance(pc[2], int) or not isinstance(pc[1], int):
    try:
        t_n = int(pc[2])
        t_n = int(pc[1])
    except Exception as e:
        await session.send("类型转换错误，请检查参数")
        return

    dpc = {
        'type': pc[0],
        'total_num': pc[1],
        'error_num': pc[2],
        'gain': None if len(pc) <= 3 else pc[3],
        'comments': None if len(pc) <= 4 else pc[4],
        'time': datetime.now().strftime("%Y-%m-%d") if len(pc) <= 5 else pc[5],
        'pid': 'No matter'
    }
    row_id = practiceDao.add(dpc)
    total_num, error_num = practiceDao.get_today_practice_num()
    await session.send(f'''添加成功，pid：{row_id}
今日做题数量：{total_num}，错题数：{error_num}''')


@on_command('queryAll', aliases={'全部练习'})
async def queryAll(session: CommandSession):
    page = session.current_arg.strip()
    if page:
        try:
            t_n = int(page)
        except Exception as e:
            await session.send("类型转换错误，请检查参数")
            return
        tmp = practiceDao.find_all(t_n)
    else:
        tmp = practiceDao.find_all()
    await session.send(tmp)


@on_command('queryPractice', aliases={'查询练习'})
async def queryPractice(session: CommandSession):
    pid = session.current_arg_text.strip()
    ret = practiceDao.find_practice(pid)
    ret = ret if len(ret) > 0 else "未查询到该练习"
    await session.send(ret)


@on_command('queryToday', aliases={'今日练习'})
async def queryToday(session: CommandSession):
    today = datetime.now().strftime("%Y-%m-%d")
    ret = practiceDao.find_day(today)
    total_num, error_num = practiceDao.get_today_practice_num()
    await session.send(f'''今日总题数：{total_num}，错题数：{error_num}
''' + ret)


@on_command('deletePrac', aliases={'删除练习'})
async def queryToday(session: CommandSession):
    pid = session.current_arg_text.strip()
    await session.send(practiceDao.delete(pid))


@nonebot.scheduler.scheduled_job('cron', hour='8', jitter=300)
async def _():
    bot = nonebot.get_bot()
    msg = get_left_days()
    await bot.send_private_msg(user_id=SUPERUSERS[0], message=msg)
