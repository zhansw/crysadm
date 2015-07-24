__author__ = 'powergx'
import config, socket, redis
import threading
import time
import requests
import json
from login import login
from datetime import datetime, timedelta


conf = None
if socket.gethostname() == 'GXMBP.local':
    conf = config.DevelopmentConfig
elif socket.gethostname() == 'iZ23bo17lpkZ':
    conf = config.ProductionConfig
else:
    conf = config.TestingConfig

redis_conf = conf.REDIS_CONF
pool = redis.ConnectionPool(host=redis_conf.host, port=redis_conf.port, db=redis_conf.db)
r_session = redis.Redis(connection_pool=pool)


def get_data(username, auto_collect):
    user_data = dict()
    for user_id in r_session.smembers('accounts:%s' % username):
        account_key = 'account:%s:%s' % (username, user_id.decode('utf-8'))

        account_info = json.loads(r_session.get(account_key).decode('utf-8'))

        if not account_info.get('active'):
            continue
        session_id = account_info.get('session_id')
        user_id = account_info.get('user_id')

        cookies = dict(sessionid=session_id, userid=str(user_id))
        if len(session_id) != 128:
            cookies['origin'] = '1'

        privilege_info = get_privilege(cookies)

        if privilege_info.get('r') != 0:

            success, account_info = relogin(account_info.get('account_name'), account_info.get('password'),
                                            account_info, account_key)
            if not success:
                continue
            session_id = account_info.get('session_id')
            user_id = account_info.get('user_id')
            cookies = dict(sessionid=session_id, userid=str(user_id))
            if len(session_id) == 128:
                cookies['origin'] = '1'
            privilege_info = get_privilege(cookies)

        #自动收取
        if datetime.now().strftime('%H:%M') in ['23:59', '00:00'] and auto_collect:
            collect(cookies)
        #自动收取

        mine_info = get_mine_info(cookies)
        zqb = get_device_stat('1', cookies)
        old = get_device_stat('0', cookies)
        ext_device_info = get_device_info(user_id)

        account_data_key = account_key + ':data'
        account_data = dict()
        account_data['updated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_data['mine_info'] = mine_info
        account_data['privilege'] = privilege_info
        account_data['dev_info'] = fill_info(zqb, ext_device_info)
        account_data['cm_info'] = fill_info(old, ext_device_info)
        account_data['dev_info']['speed_stat'] = get_speed_stat('1', cookies)
        account_data['cm_info']['speed_stat'] = get_speed_stat('0', cookies)

        user_data[user_id] = account_data
        r_session.set(account_data_key, json.dumps(account_data))

    save_history(username, user_data)


def save_history(username, user_data):
    if datetime.now().strftime('%H:%M') in ['23:59', '00:00']:
        return
    str_today = datetime.now().strftime('%Y-%m-%d')
    key = 'user_data:%s:%s' % (username, str_today)
    b_today_data = r_session.get(key)
    today_data = dict()

    if b_today_data is not None:
        today_data = json.loads(b_today_data.decode('utf-8'))

    today_data['updated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today_data['pdc'] = 0
    today_data['last_speed'] = 0
    today_data['speed_stat'] = list()
    for data in user_data.values():
        today_data.get('speed_stat').append(dict(mid=data.get('privilege').get('mid'),
                                                 dev_speed=data.get('dev_info').get('speed_stat'),
                                                 pc_speed=data.get('cm_info').get('speed_stat')))
        today_data['pdc'] += data.get('mine_info').get('dev_m').get('pdc') + data.get('mine_info').get('dev_pc').get(
            'pdc')
        for device in data.get('cm_info').get('info'):
            if device.get('ext_info') is None:
                today_data['last_speed'] += int(device.get('s') / 8)
            else:
                today_data['last_speed'] += int(device.get('ext_info').get('CUR_UPLOAD_SPEED') / 1024)
        for device in data.get('dev_info').get('info'):
            if device.get('ext_info') is None:
                today_data['last_speed'] += int(device.get('s') / 8)
            else:
                today_data['last_speed'] += int(device.get('ext_info').get('CUR_UPLOAD_SPEED') / 1024)

    r_session.set(key, json.dumps(today_data))
    r_session.expire(key, 3600*24*35)


def fill_info(device, ext_device_info):
    for device_info in device.get('info'):
        for ext_device in ext_device_info.get('DEVICE_INFO'):
            if device_info.get('dv_id') == ext_device.get('DCDNID'):
                device_info['ext_info'] = ext_device
                break

    return device


def get_device_info(user_id):
    url = 'http://webmonitor.dcdn.sandai.net/query_device?USERID=%s' % user_id
    r = requests.get(url, verify=False)

    return json.loads(r.text)


def relogin(username, password, account_info, account_key):
    login_result = login(username, password,conf.ENCRYPT_PWD_URL)

    if login_result.get('errorCode') != 0:
        account_info['status'] = login_result.get('errorDesc')
        account_info['active'] = False
        r_session.set(account_key, json.dumps(account_info))
        return False, account_info

    account_info['session_id'] = login_result.get('sessionID')

    r_session.set(account_key, json.dumps(account_info))
    return True, account_info


def get_mine_info(cookies):
    body = dict(hand='0', v='2', ver='1')
    r = requests.post('https://red.xunlei.com/?r=mine/info', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_speed_stat(s_type, cookies):

    body = dict(type=s_type, hand='0', v='0', ver='1')
    r = requests.post('https://red.xunlei.com/?r=mine/speed_stat', data=body, verify=False, cookies=cookies)
    return json.loads(r.text).get('sds')


def get_privilege(cookies):
    body = 'hand=0&v=1&ver=1'
    r = requests.post('https://red.xunlei.com/?r=usr/privilege', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_device_stat(s_type, cookies):
    url = 'https://red.xunlei.com/?r=mine/devices_stat&hand=0&type=%s&v=2&ver=1' % s_type
    this_cookies = cookies.copy()
    if len(this_cookies.get('sessionid')) != 128:
        this_cookies['origin'] = "2"
    r = requests.post(url=url, verify=False, cookies=this_cookies)

    return json.loads(r.text)


def collect(cookies):
    r = requests.get('https://red.xunlei.com/index.php?r=mine/collect', verify=False, cookies=cookies)
    return json.loads(r.text)


def get_crystal_data(username):
    while True:
        user_key = '%s:%s' % ('user', username)
        user_info = json.loads(r_session.get(user_key).decode('utf-8'))
        refresh_interval = 30 if user_info.get('refresh_interval') is None else user_info.get('refresh_interval')
        if not user_info.get('active'):
            break

        auto_collect = False
        if user_info.get('auto_collect') is not None:
            auto_collect = user_info.get('auto_collect')

        threading.Thread(target=get_data, args=(username, auto_collect), name=username).start()
        time.sleep(refresh_interval)

        #time.sleep(9999)


def start_rotate():
    thread_list = list()
    while True:
        users = r_session.smembers('users')
        for i, thread in enumerate(thread_list):
            if not thread.is_alive():
                thread_list.pop(i)
                continue
            b_name = bytes(thread.name, 'utf-8')
            if b_name in users:
                users.remove(b_name)

        for user in users:
            name = user.decode('utf-8')
            #if name != 'powergx':
            #    continue
            user_key = '%s:%s' % ('user', name)
            user_info = json.loads(r_session.get(user_key).decode('utf-8'))
            if not user_info.get('active'):
                continue

            t = threading.Thread(target=get_crystal_data, args=(name,), name=name)
            thread_list.append(t)
            t.start()

        time.sleep(30)


if __name__ == '__main__':
    start_rotate()

"""
拾取日志
POST https://red.xunlei.com/?r=usr/assetio HTTP/1.1
Host: red.xunlei.com
Proxy-Connection: keep-alive
Accept: */*
Accept-Encoding: gzip, deflate
Content-Length: 14
Content-Type: application/x-www-form-urlencoded
Accept-Language: zh-Hans;q=1, en;q=0.9
Cookie: lgname=powergx@gmail.com; origin=2; sessionid=05650B3F48D9667A1E25720B62B7910F; userid=266244981; username=powergx
Connection: keep-alive
User-Agent: RedCrystal/1.5.0 (iPhone; iOS 8.4; Scale/2.00)

p=0&ps=20&tp=0


水晶余额
GET https://red.xunlei.com/index.php?r=usr/getinfo&v=1&jsoncallback=jsonp1437727105223_280&_rnd1437727105223_280=1437727105223_280 HTTP/1.1
Accept: */*
Referer: https://red.xunlei.com/index.php?r=collect
Accept-Language: zh-CN
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729)
Host: red.xunlei.com
Connection: Keep-Alive
Cookie: Hm_lvt_58da6e2cef1bd719706c77def030bbaf=1437544578,1437545700,1437546952,1437643516; ksessionid=2E7AE4482D9F1352A70C0AA859B9CC70; kuserid=266244981; origin=3; Hm_lpvt_58da6e2cef1bd719706c77def030bbaf=1437643516; downbyte=25651685951; downfile=38; isvip=0; jumpkey=A1EFA3C9EBCD50004C4E70B802F70B7B6EA3EA97B8A9174BA2F33BE704A177104D8CEA7AA211E0D9929206A2A514651BB79B63C5AC4A9B01C84A138086EF34A5C354D2B86E6A7B1DFBA34F218A681325946127C4F1440A115B50ACECE4D2078F; logintype=1; nickname=powergx; onlinetime=610433; order=0; safe=0; score=958; sessionid=7CC5FA574E46A9323A90A3CE9E5648C118C56270B2E6AD687F20388607865771B6D7F1444B2819121B94D83F44CE5DCEE14A720B8EBB7598ECB20EE6B6CB76A6; sex=u; upgrade=0; userid=266244981; usernewno=847058001; usernick=powergx; usertype=0; usrname=powergx


POST https://red.xunlei.com/?r=usr/asset HTTP/1.1
Host: red.xunlei.com
Proxy-Connection: keep-alive
Accept: */*
Accept-Encoding: gzip, deflate
Content-Length: 16
Content-Type: application/x-www-form-urlencoded
Accept-Language: zh-Hans;q=1, en;q=0.9
Cookie: lgname=powergx@gmail.com; origin=2; sessionid=05650B3F48D9667A1E25720B62B7910F; userid=266244981; username=powergx
Connection: keep-alive
User-Agent: RedCrystal/1.5.0 (iPhone; iOS 8.4; Scale/2.00)

hand=0&v=2&ver=1

"""
