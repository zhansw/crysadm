__author__ = 'powergx'
import config, socket, redis
import threading
import time
import requests
import json
from login import login
from datetime import datetime

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

        account_info['updated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_info['mine_info'] = mine_info
        account_info['privilege'] = privilege_info

        r_session.set(account_key, json.dumps(account_info))

        zqb = get_device_stat(1, account_info.get('session_id'), account_info.get('user_id'))
        old = get_device_stat(0, account_info.get('session_id'), account_info.get('user_id'))


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
    body = 'hand=0&v=2&ver=1'
    cookies = dict(sessionid=session_id, userid=str(user_id), origin="1")
    r = requests.post('https://red.xunlei.com/?r=mine/info', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_privilege(session_id, user_id):
    body = 'hand=0&v=1&ver=1'
    cookies = dict(sessionid=session_id, userid=str(user_id), origin="1")
    r = requests.post('https://red.xunlei.com/?r=usr/privilege', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_device_stat(type, session_id, user_id):
    body = 'hand=0&type=%s&v=2&ver=1' % type
    cookies = dict(sessionid=session_id, userid=user_id, origin="1")
    r = requests.post('https://red.xunlei.com/?r=mine/devices_stat', data=body, verify=False, cookies=cookies)

    return json.loads(r.text)


if __name__ == '__main__':
    while (True):
        users = r_session.smembers('users')
        for username in users:
            threading.Thread(target=get_data, args=(username.decode('utf-8'),),
                             name='get device' + username.decode('utf-8')).start()


        time.sleep(30000)

