from datetime import datetime

import nonebot
from nonebot import CommandSession
from lopop.modules.chatgpt.openai import get_response_from_openai
from .dao import qaDao
from .conversation import Conversation
from .user import User


@nonebot.on_command('gpt', aliases={'超级ai', 'chatgpt'})
async def qa(session: CommandSession):
    dao = qaDao()
    # 获取用户 ID、会话 ID和上下文
    user_id = session.ctx['user_id']
    conversation_id = dao.get_latest_conversation_id(qq=user_id)
    context = dao.get_context(conversation_id)

    question = session.current_arg_text
    if not question:
        # 获取用户发送的问题
        question = session.get('question', prompt='你想要问什么呢？')
    # 拼接上下文
    question = f'{context}{question}'

    # 将问题发送给 openai 获取答案
    answer = get_response_from_openai(question)
    # 重新保存上下文
    context += answer
    # 获取当前时间
    timestamp = datetime.now()
    coversation = Conversation(conversation_id=conversation_id, question=question, answer=context, timestamp=timestamp)
    print(conversation_id, question, context, timestamp)
    # 保存问题和答案到数据库
    dao.save_conversation(coversation)
    # 将答案发送给用户
    await session.finish(answer.strip())


@nonebot.on_command('清空会话', aliases={'clearHistory', 'clH'})
async def _(session: CommandSession):
    user_id = session.ctx['user_id']
    dao = qaDao()
    dao.regenerate_conversation_id(qq=user_id)
    await session.finish('清空成功')
