__author__ = 'powergx'
import config, socket, redis
from multiprocessing import Process
import time
import requests
import gevent
from login import login
from datetime import datetime, timedelta

requests.packages.urllib3.disable_warnings()

conf = None
if socket.gethostname() == 'GXMBP.local':
    conf = config.DevelopmentConfig
elif socket.gethostname() == 'iZ23bo17lpkZ':
    conf = config.ProductionConfig
else:
    conf = config.TestingConfig

redis_conf = conf.REDIS_CONF
pool = redis.ConnectionPool(host=redis_conf.host, port=redis_conf.port, db=redis_conf.db, password=redis_conf.password)
r_session = redis.Redis(connection_pool=pool)

debugger = False
debugger_username = '15305017096'

from api import *


def get_data(username, auto_collect):
    print(username,'start')
    start_time = datetime.now()
    for user_id in r_session.smembers('accounts:%s' % username):
        account_key = 'account:%s:%s' % (username, user_id.decode('utf-8'))

        account_info = json.loads(r_session.get(account_key).decode('utf-8'))

        if not account_info.get('active'):
            continue
        session_id = account_info.get('session_id')
        user_id = account_info.get('user_id')

        cookies = dict(sessionid=session_id, userid=str(user_id))

        mine_info = get_mine_info(cookies)

        if is_api_error(mine_info):
            return
        if mine_info.get('r') != 0:

            success, account_info = __relogin(account_info.get('account_name'), account_info.get('password'),
                                              account_info, account_key)
            if not success:
                continue
            session_id = account_info.get('session_id')
            user_id = account_info.get('user_id')
            cookies = dict(sessionid=session_id, userid=str(user_id))
            if len(session_id) == 128:
                cookies['origin'] = '1'

            mine_info = get_mine_info(cookies)

        if mine_info.get('r') != 0:
            continue
        # 自动收取
        if auto_collect:
            collect(cookies)
        # 自动收取


        red_zqb = get_device_stat('1', cookies)
        # red_old = get_device_stat('0', cookies)
        blue_device_info = get_device_info(user_id)

        if is_api_error(red_zqb) or is_api_error(blue_device_info):
            return

        account_data_key = account_key + ':data'
        exist_account_data = r_session.get(account_data_key)
        if exist_account_data is None:
            account_data = dict()
            account_data['privilege'] = get_privilege(cookies)
        else:
            account_data = json.loads(exist_account_data.decode('utf-8'))

        if account_data.get('updated_time') is not None:
            last_updated_time = datetime.strptime(account_data.get('updated_time'), '%Y-%m-%d %H:%M:%S')
            if last_updated_time.hour != datetime.now().hour:
                account_data['zqb_speed_stat'] = get_speed_stat('1', cookies)
                account_data['old_speed_stat'] = get_speed_stat('0', cookies)
        else:
            account_data['zqb_speed_stat'] = get_speed_stat('1', cookies)
            account_data['old_speed_stat'] = get_speed_stat('0', cookies)

        account_data['updated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_data['mine_info'] = mine_info
        account_data['device_info'] = __merge_device_data(red_zqb, blue_device_info)
        account_data['income'] = get_income_info(cookies)

        if is_api_error(account_data.get('income')):
            return

        r_session.set(account_data_key, json.dumps(account_data))

        if not r_session.exists('can_drawcash'):
            r = get_can_drawcash(cookies=cookies)
            if r.get('r') == 0:
                r_session.set('can_drawcash', r.get('is_tm'))
                r_session.expire('can_drawcash', 60)

    if start_time.day == datetime.now().day:
        save_history(username)
    print(username,'end')

def __merge_device_data(red_zqb, blue_device_info):
    for blue_info in blue_device_info.get('DEVICE_INFO'):
        for red_info in red_zqb.get('info'):
            if red_info.get('dv_id') == blue_info.get('DCDNID'):
                blue_info['red_info'] = red_info
                break

    return blue_device_info.get('DEVICE_INFO')


def save_history(username):
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

    for user_id in r_session.smembers('accounts:%s' % username):
        # 获取账号所有数据
        account_data_key = 'account:%s:%s:data' % (username, user_id.decode('utf-8'))
        b_data = r_session.get(account_data_key)
        if b_data is None:
            continue
        data = json.loads(b_data.decode('utf-8'))

        if datetime.strptime(data.get('updated_time'),'%Y-%m-%d %H:%M:%S') +timedelta(minutes=1) < datetime.now():
            continue
        today_data.get('speed_stat').append(dict(mid=data.get('privilege').get('mid'),
                                                 dev_speed=data.get('zqb_speed_stat') if data.get(
                                                     'zqb_speed_stat') is not None else [0] * 24,
                                                 pc_speed=data.get('old_speed_stat') if data.get(
                                                     'old_speed_stat') is not None else [0] * 24))
        today_data['pdc'] += data.get('mine_info').get('dev_m').get('pdc') + \
                             data.get('mine_info').get('dev_pc').get('pdc')

        today_data['balance'] += data.get('income').get('r_can_use')
        today_data['income'] += data.get('income').get('r_h_a')
        for device in data.get('device_info'):
            today_data['last_speed'] += int(device.get('CUR_UPLOAD_SPEED') / 1024)

    r_session.set(key, json.dumps(today_data))
    r_session.expire(key, 3600 * 24 * 35)


def __relogin(username, password, account_info, account_key):
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


def start_rotate():
    if r_session.exists('api_error_info'):
        return

    users = r_session.smembers('users')
    g_list = []
    for user in users:
        username = user.decode('utf-8')
        if username != debugger_username and debugger:
            continue
        user_key = '%s:%s' % ('user', username)
        user_info = json.loads(r_session.get(user_key).decode('utf-8'))
        if not user_info.get('active'):
            continue

        if datetime.now().strftime('%H:%M') in ['23:59', '00:00'] or debugger:
            every_day_night(user_info, username)

        if not r_session.exists('user:%s:is_online' % username) and not debugger:
            continue

        if r_session.exists('user:%s:is_querying' % username) and not debugger:
            continue

        r_session.set('user:%s:is_querying' % username, '1')
        r_session.expire('user:%s:is_querying' % username, 5)
        g_list.append(gevent.spawn(get_data, username, False))
    if len(g_list) > 0:
        gevent.joinall(g_list)


def every_day_night(user_info, username):
    auto_collect = user_info.get('auto_collect') if user_info.get('auto_collect') is not None else False
    r_session.set('user:%s:is_querying' % username, '1')
    r_session.expire('user:%s:is_querying' % username, 30)
    gevent.spawn(get_data, username, auto_collect).join()


if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_socket()
    monkey.patch_ssl()
    while True:
        Process(target=start_rotate).start()
        if debugger:
            time.sleep(400)
        time.sleep(4)
