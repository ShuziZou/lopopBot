import re

from nonebot import on_command, CommandSession
from nonebot import permission

from .image_to_words import do_i2w
from .translate import do_translate

sv_help = '''
百度智能云相关接口
【翻译】 需要翻译的语句
【图片转文字】(或者i2w) 图片
'''.strip()

quit_command = ['quit', '退出']


@on_command('帮助')
async def _(sess: CommandSession):
    await sess.send(f'{sv_help}')


@on_command('翻译', aliases={'fy', 'translate'}, permission=permission.SUPERUSER)
async def _(sess: CommandSession):
    content = sess.current_arg
    print(content)
    if not content:
        content = await sess.aget(prompt='请输入待翻译语句')
        if content in quit_command:
            return
    sentences = do_translate(content)
    ans = ''
    for s in sentences:
        ans += s['dst'] + ' '
    await sess.finish(message=ans)


@on_command('图片转文字', aliases={'image2words', 'i2w'})
async def _(session: CommandSession):
    image = await session.aget('image', prompt='请发送待转文字的图片')
    msg = f'''接收到的图片：
{image}
正在处理...
格式有误！请检查发送内容'''
    try:
        image_url = re.match('\[(.*)?url=(.*)?]', image).group(2)
        print(image_url)
        words_result: dict = do_i2w(image_url)
        words = []
        for word_dict in words_result:
            words.append(word_dict['words'])
        msg = '\n'.join(words)
    except Exception as e:
        print(e)
    await session.finish(message=msg)
