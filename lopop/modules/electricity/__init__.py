from nonebot import on_command, CommandSession, permission


@on_command('electricity', aliases=('电表', '查电表', '剩余电量'), permission=permission.SUPERUSER)
async def electricity(session: CommandSession):
    meter = session.current_arg_text.strip()
    if not meter:
        meter = (await session.aget(prompt='你想查询哪个电表呢？')).strip()
        while not meter:
            meter = (await session.aget(prompt='要查询的电表不能为空呢，请重新输入')).strip()
    # electricity_report = await get_electricity_of_city(meter)
    await session.send(f'您要查的电表是{meter}')
