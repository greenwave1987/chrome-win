# -*- coding: utf-8 -*-
'''
脚本说明：
'''
import sys
import os  #读取配置文件
import json  #读取配置文件
import aiohttp   #用于请求青龙
import re
#from datetime import datetime #获取时间
import asyncio  # 异步I/O操作库
from urllib.parse import unquote

async def print_message(message):     #初始化异步print
    print(message)

# 获取pin
cookie_findall=re.compile(r'pt_pin=(.+?);')
def get_pin(cookie):
    try:
        return unquote(cookie_findall.findall(cookie)[0])
    except:
        print('ck格式不正确，请检查')

async def getck():                           #判断有没有配置文件

    cookie={}
    cookie_list=os.environ["JD_COOKIE"].split('&')       # 获取cookie_list的合集
    ##print(cookie_list)
    for ck in cookie_list:                              #找所有网页所有的cookie数据
        pin=get_pin(ck)
        ##print(f"查验{pin}环境变量：")  
        cookie[pin]=ck
    ##print(cookie)
    return cookie
    
        

async def getqlinfo():                           #判断有没有配置文件
    qlinfo = None   #初始化变量
    configfile = 'qlinfo.ini'     #配置文件名称为
    if not os.path.exists(configfile):     #看看有没有配置文件
        print('无配置文件，退出！')
    else:
        with open(configfile, 'r', encoding='utf-8') as file:
            qlinfo = json.load(file)
            file.close()  # 关闭文件

        return(qlinfo)
        ##qlinfo = json.loads(qlinfo)  # 使用 json模块读取
        ##print(qlinfo)

async def initql(qlinfo):        #初始化青龙并获取青龙的token
    qlip = None   #初始化变量
    client_id = None   #初始化变量
    client_secret = None   #初始化变量

    try:
        
        if qlinfo['ip']:
            qlip = qlinfo['ip']        #找配置文件中qlip=的值并赋予qlip
        if qlinfo['client_id']:
            client_id = qlinfo['client_id']       #同上
        if qlinfo['client_secret']:
            client_secret = qlinfo['client_secret']     #同上

        if not qlip or not client_id or not client_secret:         #如果没有三个参数变量没有值，就报下面的错误，单个检测报错
            if not qlip:
                print('青龙IP配置出错，请确认配置文件')
                await asyncio.sleep(10)  # 等待10秒，等待
            if not client_id:
                print('青龙client_id配置出错，请确认配置文件')
                await asyncio.sleep(10)  # 等待10秒，等待
            if not client_secret:
                print('青龙client_secret配置出错，请确认配置文件')
                await asyncio.sleep(10)  # 等待10秒，等待
            raise SystemExit

        async with aiohttp.ClientSession() as session:                #获取青龙的token
            async with session.get(f"{qlip}/open/auth/token?client_id={client_id}&client_secret={client_secret}") as response:
                dicts = await response.json()
                if dicts:
                    print('已连接青龙容器...')
                else:
                    print(dicts)
            return dicts['data']['token']
    except Exception as e:
        print(f"连接青龙发生异常，请确认配置文件：{e}")
        await asyncio.sleep(10)  # 等待10秒，等待
        raise SystemExit

async def qlenvs(qlinfo):   #获取青龙全部jdck变量
    jd_cookie_data={}
    try:
        async with aiohttp.ClientSession() as session:                              # 异步操作命令
            url = f"{qlinfo['ip']}/open/envs?searchValue="                   #设置设置连接
            headers = {'Authorization': 'Bearer ' + qltoken}                         #设置api的headers请求头
            async with session.get(url, headers=headers) as response:                              #获取变量请求
                rjson = await response.json()                             #解析返回的json数据
                if rjson['code'] == 200:                                #如果返回code200,根据青龙api文档
                    for env in rjson['data']:
                        if env.get('name') == 'JD_COOKIE':
                            pin=get_pin(env["value"])
                            jd_cookie_data[pin] = env
                    ##jd_cookie_data = {env for env in rjson['data'] if env.get('name') == 'JD_COOKIE'}            #获取全部jd的变量

                    
                    return jd_cookie_data
                else:
                    print(f"获取环境变量失败：{rjson['message']}")
    except Exception as e:
        print(f"获取环境变量失败：{str(e)}")



def load_send():
    global send
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
        except:
            send = False
            print("加载通知服务失败~")
    else:
        send = False
        print("加载通知服务失败~")







async def logon_main(qlinfo,ckinfo):             #读取配置文件账户密码，登录
    
    global qltoken   #初始化青龙获取青龙ck
    global envs               #青龙环境全局变量
    qltoken = await initql(qlinfo)      #初始化青龙token

    envs = await qlenvs(qlinfo)   #获取青龙环境变量(仅JC_COOKIE)
    ##print(envs)

    await SubmitCK(qlinfo,ckinfo)  #提交ck



async def SubmitCK(qlinfo,ckinfo):  #提交ck

    text = f"共有{len(ckinfo)} 个CK。\n" 
    text += f"{qlinfo['ip']}有{len(envs)} 个账号：\n" 
    for pin in qlinfo['pin_list']:
    ##for env in envs:
        found_ddhhs = False                             #初始化循环变量，用于后面找不到变量的解决方式
        ##pin=get_pin(env["value"])
        ##if pin in qlinfo['pin_list']:     #在所有变量值中找remarks，找到执行下面的更新ck
        ##if pin in env["remarks"]:      #在所有变量值中找remarks，找到执行下面的更新ck
        if envs.get(pin) :
            found_ddhhs = True                             #把变量设为True，停下循环
            env=envs.get(pin)
            if env['status']!=0:
                envid = env["id"]                             #把找到的id设为envid的变量值
                remarks = env["remarks"]                             #同上
                data = {
                    'name': "JD_COOKIE",
                    'value': ckinfo[pin],
                    "remarks": remarks,
                    "id": envid,
                }                             #提交青龙的数据
                async with aiohttp.ClientSession() as session:                             #下面是提交
                    url = f"{qlinfo['ip']}/open/envs"
                    async with session.put(url, headers={'Authorization': 'Bearer ' + qltoken}, json=data) as response:            #更新变量的api
                        rjson = await response.json()
                        if rjson['code'] == 200:
                            url2 = f"{qlinfo['ip']}/open/envs/enable"
                            data2 = [
                                envid
                            ]
                            async with session.put(url2, headers={'Authorization': 'Bearer ' + qltoken}, json=data2) as response:            #启用变量的api
                                rjson2 = await response.json()
                                if rjson2['code'] == 200:
                                    print(f"更新{pin}环境变量成功")
                                    text += f"更新{pin}环境变量成功\n"

                                else:
                                    print(f"启用{pin}环境变量失败：{rjson['message']}")
                                    text += f"启用{pin}环境变量失败：{rjson['message']}\n"

                        else:
                            print(f"更新{pin}环境变量失败：{rjson['message']}")
                            text += f"更新{pin}环境变量失败：{rjson['message']}\n"

            else:
                print(f"{pin}有效，不更新！")
                text += f"{pin}有效，不更新！\n"

        if not found_ddhhs:          #如果没找到pt_pin，执行下面的新建ck，以下同上，只是新建不是更新
            data = [
                {
                    'name': "JD_COOKIE",
                    'value': ckinfo[pin],
                    "remarks": pin,
                }
            ]
            async with aiohttp.ClientSession() as session:
                url = f"{qlinfo['ip']}/open/envs"
                async with session.post(url, headers={'Authorization': 'Bearer ' + qltoken}, json=data) as response:
                    rjson = await response.json()
                    if rjson['code'] == 200:
                        print(f"新建{pin}环境变量成功")
                        text += f"新建{pin}环境变量成功\n"

                    else:
                        print(f"新建{pin}环境变量失败：{rjson['message']}")
                        text += f"新建{pin}环境变量失败：{rjson['message']}\n"

    send('自动更新CK',text)


async def main():  # 打开并读取配置文件，主程序
    load_send()
    await print_message('当前版本：20240612')

    ckinfo=await getck()
    ##print(ckinfo)

    qlinfo=await getqlinfo()
    ##print(qlinfo)

    for info in qlinfo:                              #找所有网页所有的cookie数据
        print(f"\n查验{info}环境变量：")  
        await logon_main(qlinfo[info],ckinfo)    #登录操作，写入ck到文件

    await print_message('\n完成全部更新')
    await asyncio.sleep(10)  # 等待10秒，等待

asyncio.get_event_loop().run_until_complete(main())  #使用异步I/O循环运行main()函数，启动整个自动登录和滑块验证流程。
