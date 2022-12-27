import json
import requests


async def get_electricity_of_city(meter: str) -> str:
    location = meter.split('-')
    office = location[0]
    room = location[1]
    meter_id = 301071022040 + (int(office) - 204)*4+int(room)
    headers = {
        'Cookie': '.AspNetCore.Wechat_Authentication_Scheme=CfDJ8IghTRDBbXdBoUcsjD0RvWrULL_E5QP7TyyoJvcaTUv0vzZuBhvQZmM5iSabGzajA3tkZz8PLsTRx1CZrR6f3mG8_ajlFzKT32VHtApU_HaJpPVqzy-OuxI5Ytapvjxup217mkRQOJRWT-EandsA4gBzRET07EfsrriJJGiPpqx6pDfUwPlHJw8Ss_aK42x630EX_64_ty1cQM6SWwf8mAoXC9jvO48lvHmb0NAZF4IkNAHeUnvp5atJkvw_1tW612tTrMYZm3WaVO6RCerkxh5vifZkM-iQGDVOem86vxneYeMw1QUgJDRVHonk5J4iTwqgLlpWZLb0rgKJCROjoJlDAf2kRH5Th3AGM6pbA4ydb-UkMoxayNln_ZrYZJV5enq1GYOoreVryYFhvYwrZSVNYqiNomzb5V-IyRnUD1a5VgWpdi3L4P01QXFBwoJHfqC81OihIqvEg-VkC7lH2C6vnEPUz0obkzZNncS7kiMkMkYSArtHnfKfttktNahgylgLNN-UaZJKfrrhSD1eQ5Is81pt3c7E-WIvAVTk5fSLT_5g_PMQP-pWlbQ0-6LAzLCJ4IjQ4i58AmBTXe0k8JxH0CC26XsfGcdoKMqV15Xy_GlYdUqvpktMMCJA1U4MqbD7d0kI5bWuEQfoXV0buQ1oV9oWcZ6ovNXNJS5dwLwDyvrRZqsE4KBClljBgX_E5Q'
    }
    rep = requests.get(
        f'http://wx.hezhonghuineng.com/api/common/reading?id={meter_id}', headers=headers)
    data = rep.text
    data = json.loads(data)
    return f'{meter}截至{data["remainingTime"]}的剩余电量为{data["remaining"]}，本月用电{data["power"]}{data["powerUnit"]}'

# if __name__ == '__main__':
#     resp = get_electricity_of_city('204-2')
#     print(resp)
