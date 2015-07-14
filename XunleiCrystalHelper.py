__author__ = 'powergx'
import config, socket, redis
import threading
import time
import requests
import json

conf = None
if socket.gethostname() == 'GXMBP.local':
    conf = config.DevelopmentConfig
elif socket.gethostname() == 'iZ23bo17lpkZ':
    conf = config.ProductionConfig
else:
    conf=config.TestingConfig

redis_conf = conf.REDIS_CONF
pool = redis.ConnectionPool(host=redis_conf.host, port=redis_conf.port, db=redis_conf.db)
r_session = redis.Redis(connection_pool=pool)


def get_data(username):
    for user_id in r_session.smembers('accounts:%s' % username):
        account_key = 'account:%s:%s' % (username, user_id)
        account_info = json.loads(r_session.get(account_key).decode('utf-8'))
        if not account_info.get('active'):
            continue
        get_device_stat(1,account_info.get('session_id'))
        get_device_stat(0,account_info.get('session_id'))

def get_device_stat(type,session_id):
    """
    POST https://red.xunlei.com/?r=mine/devices_stat HTTP/1.1
    Host: red.xunlei.com
    Proxy-Connection: keep-alive
    Accept: */*
    Accept-Encoding: gzip, deflate
    Content-Length: 23
    Content-Type: application/x-www-form-urlencoded
    Accept-Language: zh-Hans;q=1, en;q=0.9
    Cookie: lgname=powergx@gmail.com; origin=2; sessionid=32079C8670AAD004FF40AFAED2ABFD76; userid=266244981; username=powergx
    Connection: keep-alive
    User-Agent: RedCrystal/1.5.0 (iPhone; iOS 8.4; Scale/2.00)

    hand=0&type=0&v=2&ver=1
    """
    pass

if __name__ == '__main__':
    while(True):
        users = r_session.smembers('users')
        for username in users:
            threading.Thread(target=get_data, args=(username, ), name='get device' + username).start()

        time.sleep(10)

