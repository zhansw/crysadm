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


def get_data(username):
    user_data = dict()
    for user_id in r_session.smembers('accounts:%s' % username):
        account_key = 'account:%s:%s' % (username, user_id.decode('utf-8'))
        account_info = json.loads(r_session.get(account_key).decode('utf-8'))
        if not account_info.get('active'):
            continue
        session_id = account_info.get('session_id')
        user_id = account_info.get('user_id')

        privilege_info = get_privilege(session_id, user_id)
        if privilege_info.get('r') != 0:
            success, account_info = relogin(account_info.get('account_name'), account_info.get('password'),
                                            account_info, account_key)
            if not success:
                continue
            session_id = account_info.get('session_id')
            user_id = account_info.get('user_id')
            privilege_info = get_privilege(session_id, user_id)

        mine_info = get_mine_info(session_id, user_id)
        zqb = get_device_stat('1', session_id, user_id)
        old = get_device_stat('0', session_id, user_id)
        ext_device_info = get_device_info(user_id)

        account_data_key = account_key + ':data'
        account_data = dict()
        account_data['updated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_data['mine_info'] = mine_info
        account_data['privilege'] = privilege_info
        account_data['dev_info'] = fill_info(zqb, ext_device_info)
        account_data['cm_info'] = fill_info(old, ext_device_info)

        user_data[user_id] = account_data
        r_session.set(account_data_key, json.dumps(account_data))

    save_history(username, user_data)


def save_history(username, user_data):
    if datetime.now().strftime('%H:%M:') == '23:59' or datetime.now().strftime('%H:%M:') == '00:00':
        return
    str_today = datetime.now().strftime('%Y-%m-%d')
    key = 'user_data:%s:%s' % (username, str_today)
    today_data = dict(pdc=0, last_speed=0)

    for data in user_data.values():
        today_data['pdc'] += data.get('mine_info').get('dev_m').get('pdc') + data.get('mine_info').get('dev_pc').get('pdc')
        for device in data.get('cm_info').get('info'):
            if device.get('ext_info') is None:
                today_data['last_speed'] += int(device.get('s')/8)
            else:
                today_data['last_speed'] += int(device.get('ext_info').get('CUR_UPLOAD_SPEED')/1024)
        for device in data.get('dev_info').get('info'):
            if device.get('ext_info') is None:
                today_data['last_speed'] += int(device.get('s')/8)
            else:
                today_data['last_speed'] += int(device.get('ext_info').get('CUR_UPLOAD_SPEED')/1024)

    r_session.set(key, json.dumps(today_data))


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
    login_result = login(username, password)
    if login_result.get('errorCode') != 0:
        account_info['status'] = login_result.get('errorDesc')
        account_info['active'] = False
        r_session.set(account_key, json.dumps(account_info))
        return False, account_info

    account_info['session_id'] = login_result.get('sessionID')

    r_session.set(account_key, json.dumps(account_info))
    return True, account_info


def get_mine_info(session_id, user_id):
    cookies = dict(sessionid=session_id, userid=str(user_id), origin="1")
    body = dict(hand='0', v='2', ver='1')
    r = requests.post('https://red.xunlei.com/?r=mine/info', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_privilege(session_id, user_id):
    body = 'hand=0&v=1&ver=1'
    cookies = dict(sessionid=session_id, userid=str(user_id), origin="1")
    r = requests.post('https://red.xunlei.com/?r=usr/privilege', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_device_stat(type, session_id, user_id):
    url = 'https://red.xunlei.com/?r=mine/devices_stat&hand=0&type=%s&v=2&ver=1' % type
    cookies = dict(sessionid=session_id, userid=user_id, origin="2")
    r = requests.post(url=url, verify=False, cookies=cookies)

    return json.loads(r.text)


def get_crystal_data(username):
    while True:
        user_key = '%s:%s' % ('user', username)
        user_info = json.loads(r_session.get(user_key).decode('utf-8'))
        refresh_interval = 30 if user_info.get('refresh_interval') is None else user_info.get('refresh_interval')
        if not user_info.get('active'):
            break

        threading.Thread(target=get_data, args=(username,), name=username).start()
        time.sleep(refresh_interval)


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


