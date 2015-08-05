__author__ = 'powergx'
import config, socket, redis
import threading
import time
import requests
import json
from login import login
from datetime import datetime, timedelta
from api import *


requests.packages.urllib3.disable_warnings()

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

        mine_info = get_mine_info(cookies)
        if mine_info.get('r') != 0:

            success, account_info = relogin(account_info.get('account_name'), account_info.get('password'),
                                            account_info, account_key)
            if not success:
                continue
            session_id = account_info.get('session_id')
            user_id = account_info.get('user_id')
            cookies = dict(sessionid=session_id, userid=str(user_id))
            if len(session_id) == 128:
                cookies['origin'] = '1'

            mine_info = get_mine_info(cookies)

        # 自动收取
        if datetime.now().strftime('%H:%M') in ['23:59', '00:00'] and auto_collect:
            collect(cookies)
        # 自动收取


        red_zqb = get_device_stat('1', cookies)
        # red_old = get_device_stat('0', cookies)
        blue_device_info = get_device_info(user_id)

        account_data_key = account_key + ':data'
        exist_account_data = r_session.get(account_data_key)
        if exist_account_data is None:
            account_data = dict()
            account_data['privilege'] = get_privilege(cookies)
        else:
            account_data = json.loads(exist_account_data.decode('utf-8'))

        if account_data.get('updated_time') is not None:
            last_updated_time = datetime.strptime(account_data.get('updated_time'),'%Y-%m-%d %H:%M:%S')
            if last_updated_time.hour != datetime.now().hour:
                account_data['zqb_speed_stat'] = get_speed_stat('1', cookies)
                account_data['old_speed_stat'] = get_speed_stat('0', cookies)
        else:
            account_data['zqb_speed_stat'] = get_speed_stat('1', cookies)
            account_data['old_speed_stat'] = get_speed_stat('0', cookies)

        account_data['updated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_data['mine_info'] = mine_info
        account_data['device_info'] = merge_device_data(red_zqb, blue_device_info)
        account_data['income'] = get_income_info(cookies)

        user_data[user_id] = account_data
        r_session.set(account_data_key, json.dumps(account_data))

        if not r_session.exists('can_drawcash'):
            r = get_can_drawcash(cookies=cookies)
            if r.get('r') == 0:
                r_session.set('can_drawcash', r.get('is_tm'))
                r_session.expire('can_drawcash', 60)

    save_history(username, user_data)


def merge_device_data(red_zqb, blue_device_info):
    for blue_info in blue_device_info.get('DEVICE_INFO'):
        for red_info in red_zqb.get('info'):
            if red_info.get('dv_id') == blue_info.get('DCDNID'):
                blue_info['red_info'] = red_info
                break

    return blue_device_info.get('DEVICE_INFO')


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
    today_data['balance'] = 0
    today_data['income'] = 0
    today_data['speed_stat'] = list()
    for data in user_data.values():
        today_data.get('speed_stat').append(dict(mid=data.get('privilege').get('mid'),
                                                 dev_speed=data.get('zqb_speed_stat'),
                                                 pc_speed=data.get('old_speed_stat')))
        today_data['pdc'] += data.get('mine_info').get('dev_m').get('pdc') + \
                             data.get('mine_info').get('dev_pc').get('pdc')

        today_data['balance'] += data.get('income').get('r_can_use')
        today_data['income'] += data.get('income').get('r_h_a')
        for device in data.get('device_info'):
            today_data['last_speed'] += int(device.get('CUR_UPLOAD_SPEED') / 1024)

    r_session.set(key, json.dumps(today_data))
    r_session.expire(key, 3600 * 24 * 35)


def relogin(username, password, account_info, account_key):
    login_result = login(username, password, conf.ENCRYPT_PWD_URL)

    if login_result.get('errorCode') != 0:
        account_info['status'] = login_result.get('errorDesc')
        account_info['active'] = False
        r_session.set(account_key, json.dumps(account_info))
        return False, account_info

    account_info['session_id'] = login_result.get('sessionID')
    account_info['status'] = 'OK'
    r_session.set(account_key, json.dumps(account_info))
    return True, account_info


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
            #   continue
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
