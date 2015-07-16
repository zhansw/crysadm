__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app, r_session
from auth import requires_admin, requires_auth
import json
import requests


@app.route('/excavators')
@requires_auth
def excavators():
    user = session.get('user_info')
    err_msg = None
    if session.get('error_message') is not None:
        err_msg = session.get('error_message')
        session['error_message'] = None

    accounts_key = 'accounts:%s' % user.get('username')
    account_set = r_session.smembers(accounts_key)
    accounts = list()

    for acct in account_set:
        account_key = 'account:%s:%s' % (user.get('username'), acct.decode("utf-8"))
        account_info = json.loads(r_session.get(account_key).decode("utf-8"))
        accounts.append(account_info)
        print(account_info)

    return render_template('excavators.html', err_msg=err_msg, accounts=accounts)

@app.route('/collect/<user_id>', methods=['POST'])
@requires_auth
def collect_all(user_id):
    user = session.get('user_info')
    account_key = 'account:%s:%s' % (user.get('username'), user_id)
    account_info = json.loads(r_session.get(account_key).decode("utf-8"))

    session_id = account_info.get('session_id')
    user_id = account_info.get('user_id')

    cookies = dict(sessionid=session_id, userid=str(user_id), origin="1")
    r = requests.get('https://red.xunlei.com/index.php?r=mine/collect', verify=False, cookies=cookies)

    account_info.get('mine_info')['td_not_in_a'] = 0
    r_session.set(account_key, json.dumps(account_info))
    """
    GET https://red.xunlei.com/index.php?r=mine/collect HTTP/1.1
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Host: red.xunlei.com
    Cookie: sessionid=45924D1377FF4495F56777E089A00F48; userid=266244981; origin=1
    Connection: Close

    :return:
    """
    return redirect(url_for('excavators'))