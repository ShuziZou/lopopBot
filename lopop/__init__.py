import os

import nonebot
from hoshino import HoshinoBot, log
from . import config

_bot = None
logger = log.new_logger('lopop', config.DEBUG)


def init() -> HoshinoBot:
    global _bot
    nonebot.init(config)
    _bot = nonebot.get_bot()

    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'modules'),
        'lopop.modules')

    return _bot
