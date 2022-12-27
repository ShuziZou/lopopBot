import requests
import json
import time

from nonebot import CommandSession


async def reserveSeat(sess: CommandSession, cookie, maxRetryTimes=3):
    myheaders = {'Host': 'wechat.v2.traceint.com', 'Connection': 'keep-alive', 'Content-Length': '729',
                 'User-Agent': 'Mozilla/5.0 (Linux; Android 11; M2012K11AC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3149 MMWEBSDK/20211001 Mobile '
                               'Safari/537.36 MMWEBID/68 MicroMessenger/8.0.16.2040(0x28001053) Process/toolsmp '
                               'WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
                 'Content-Type': 'application/json', 'Accept': '*/*', 'Origin': 'https://web.traceint.com',
                 'X-Requested-With': 'com.tencent.mm', 'Sec-Fetch-Site': 'same-site', 'Sec-Fetch-Mode': 'cors',
                 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://web.traceint.com/web/index.html',
                 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                 }
    # with open("./cookie.json", "r", encoding="utf8") as fp:
    #     json_data_file = json.load(fp)
    #     nickname = input("请输入昵称：")
    #     ok = False
    #     for item in json_data_file["cookies"]:
    #         # if item["nickname"] == nickname:
    #         ok = True
    #         nickname = item['nickname']
    #         myheaders['Cookie'] = item['cookie']
    #         break
    #     if not ok:
    #         raise Exception("无效的昵称!")
    myheaders['Cookie'] = cookie
    tips = '''楼层\t\t\t代号\n'''
    locations = {
        "122783": "社科图书借阅室（一）",
        "122797": "一楼大厅",
        "122790": "社科图书借阅室（二）",
        "122804": "电子阅览室",
        "122818": "二楼大厅",
        "122825": "自科图书借阅室（一）",
        "122832": "社科图书借阅室（三）",
        "122839": "三楼大厅",
        "122846": "四楼A区",
        "122853": "期刊阅览室",
        "122860": "五楼大厅",
        "123301": "四楼B区",
        "123308": "四楼C区",
        "123315": "临时入馆资格"
    }
    for key in locations:
        tips += f'''{key}\t\t{locations[key]}\n'''
    try:
        libnum = int(await sess.aget(prompt=tips + "\n请输入想抢的楼层代号："))
    except:
        await sess.finish("非法数字！\n预约终止。")
        return
    # libnum = 122804
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
    s = requests.session()
    s.headers.clear()
    s.headers.update(myheaders)
    count = 1
    ''',proxies={'https': 'http://127.0.0.1:8888'}, verify=False'''
    while count < maxRetryTimes:
        print("第%d次尝试..." % count)
        count += 1
        r = s.post("https://wechat.v2.traceint.com/index.php/graphql/", json=check_library_body)
        json_data = r.json()
        # reserve_quickly.write_and_update(s, item, json_data_file, myheaders)
        ok = True
        try:
            for lib in json_data[0]['data']['userAuth']['reserve']['libs']:
                if lib['lib_id'] == libnum:
                    if lib['is_open'] and lib['lib_rt']['seats_has'] != 0:
                        break
                    else:
                        ok = False
        except:
            msg = str(json_data) + "请求图书馆房间信息失败"
            await sess.send(msg)
        if not ok:
            await sess.finish('图书馆未开放！或者该房间人已经满了！')
            return
        check_floor_body = {"operationName": "libLayout",
                            "query": "query libLayout($libId: Int, $libType: Int) {\n userAuth "
                                     "{\n reserve {\n libs(libType: $libType, libId: $libId) {"
                                     "\n lib_id\n is_open\n lib_floor\n lib_name\n lib_type\n "
                                     "lib_layout {\n seats_total\n seats_booking\n "
                                     "seats_used\n max_x\n max_y\n seats {\n x\n y\n key\n "
                                     "type\n name\n seat_status\n status\n }\n }\n }\n }\n "
                                     "}\n}", "variables": {"libId": libnum}}
        r = s.post("https://wechat.v2.traceint.com/index.php/graphql/", json=check_floor_body)
        json_data = r.json()
        # reserve_quickly.write_and_update(s, item, json_data_file, myheaders)

        ok = -1  # -1表示没有该座位， 0表示被占了， 1表示找到了且未被占
        while (ok == -1):
            try:
                seat_example = json_data[0]['data']['userAuth']['reserve']['libs'][0]['lib_layout']['seats'][0]
                await sess.send(f"最左上角的座位坐标为：{seat_example['key']}，其他的请自行悟道")
                seatkey = await sess.aget(prompt='请输入座位的具体坐标：用英文逗号隔开（如12,6）（-1退出）')
                if seatkey == "-1":
                    ok = -2
                for seat in json_data[0]['data']['userAuth']['reserve']['libs'][0]['lib_layout']['seats']:
                    if seat['key'] == seatkey:
                        if seat['seat_status'] == 1:
                            ok = 1
                        else:
                            ok = 0
                            await sess.finish('座位已经被占了')
                        break
            except:
                await sess.finish("请求座位列表失败")
                return
            if ok == -1:
                await sess.send('座位不存在')
            elif ok == 0:
                await sess.send('座位已经被占了')
        if ok == -2:
            await sess.finish('预约终止')
            return
        reserve_body = {"operationName": "reserveSeat",
                        "query": "mutation reserveSeat($libId: Int!, $seatKey: String!, "
                                 "$captchaCode: String, $captcha: String!) {\n userAuth {\n "
                                 "reserve {\n reserveSeat(\n libId: $libId\n seatKey: "
                                 "$seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n "
                                 ")\n }\n }\n}", "variables": {"seatKey": seatkey,
                                                               "libId": libnum,
                                                               "captchaCode": "",
                                                               "captcha": ""}}
        r = s.post("https://wechat.v2.traceint.com/index.php/graphql/", json=reserve_body)
        json_data = r.json()
        # reserve_quickly.write_and_update(s, item, json_data_file, myheaders)
        try:
            if json_data[0]['data']['userAuth']['reserve']['reserveSeat']:
                await sess.finish("预约成功！！")
                return seatkey
        except:
            await sess.finish("预约座位失败")
        time.sleep(1)

# if __name__ == '__main__':
#     main()
