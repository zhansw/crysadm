__author__ = 'powergx'
__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app,r_session
from auth import requires_admin, requires_auth
import json


@app.route('/login')
def login():
    if session.get('user_info') is not None:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@requires_auth
def dashboard():
    user = session.get('user_info')

    accounts_key = 'accounts:%s' % user.get('username')
    account_set = r_session.smembers(accounts_key)
    accounts = list()

    for acct in account_set:
        account_key = 'account:%s:%s' % (user.get('username'), acct.decode("utf-8"))
        account_data_key = account_key+':data'
        account_data_value = r_session.get(account_data_key)
        account_info = json.loads(r_session.get(account_key).decode("utf-8"))
        if account_data_value is not None:
            account_info['data'] = json.loads(account_data_value.decode("utf-8"))
        accounts.append(account_info)

    return render_template('dashboard.html')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/12')
def hello_world():
    """
    https://red.xunlei.com/?r=usr/queryGift HTTP/1.1
    https://red.xunlei.com/?r=usr/hand&actid=2021&hand=0&v=0&ver=1 HTTP/1.1
    https://red.xunlei.com/?r=mine/info HTTP/1.1
    https://red.xunlei.com/?r=mine/devices_stat HTTP/1.1
    https://red.xunlei.com/?r=mine/ability HTTP/1.1
    https://red.xunlei.com/?r=mine/speed_stat HTTP/1.1
    https://red.xunlei.com/?r=sys/msg HTTP/1.1
    https://red.xunlei.com/?r=usr/reportPlayTime HTTP/1.1
    https://red.xunlei.com/?r=usr/assetio HTTP/1.1


    """
    return r_session.get('test')
    cookies = dict(sessionid='C3F6EA0EA3E1A7908109D012F71D458B',userid='266244981')
    headers = {'User-Agent': 'RedCrystal/1.4.0 (iPhone; iOS 8.3; Scale/2.00)'}
    s = requests.Session()

    r = s.get('https://red.xunlei.com/?r=mine/info', cookies=cookies,headers=headers)
    print(r.text)

    print(s.get('https://red.xunlei.com/?r=mine/devices_stat', cookies=cookies,headers=headers).text)


