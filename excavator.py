__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from crysadm import app, r_session
from auth import requires_admin, requires_auth
import json
import requests
from urllib.parse import urlparse
import time


@app.route('/excavators')
@requires_auth
def excavators():
    user = session.get('user_info')
    err_msg = None
    if session.get('error_message') is not None:
        err_msg = session.get('error_message')
        session['error_message'] = None

    info_msg = None
    if session.get('info_message') is not None:
        info_msg = session.get('info_message')
        session['info_message'] = None

    accounts_key = 'accounts:%s' % user.get('username')
    accounts = list()

    for acct in sorted(r_session.smembers(accounts_key)):
        account_key = 'account:%s:%s' % (user.get('username'), acct.decode("utf-8"))
        account_data_key = account_key+':data'
        account_data_value = r_session.get(account_data_key)
        account_info = json.loads(r_session.get(account_key).decode("utf-8"))
        if account_data_value is not None:
            account_info['data'] = json.loads(account_data_value.decode("utf-8"))
        accounts.append(account_info)


    return render_template('excavators.html', err_msg=err_msg, info_msg=info_msg, accounts=accounts)

@app.route('/collect/<user_id>', methods=['POST'])
@requires_auth
def collect_all(user_id):
    user = session.get('user_info')
    account_key = 'account:%s:%s' % (user.get('username'), user_id)
    account_info = json.loads(r_session.get(account_key).decode("utf-8"))

    session_id = account_info.get('session_id')
    user_id = account_info.get('user_id')

    cookies = dict(sessionid=session_id, userid=str(user_id))
    if len(session_id) != 128:
        cookies['origin'] = '1'
    r = requests.get('https://red.xunlei.com/index.php?r=mine/collect', verify=False, cookies=cookies)

    account_data_key = account_key+':data'
    account_data_value = json.loads(r_session.get(account_data_key).decode("utf-8"))
    account_data_value.get('mine_info')['td_not_in_a'] = 0
    r_session.set(account_data_key, json.dumps(account_data_value))

    return redirect(url_for('excavators'))


@app.route('/drawcash/<user_id>', methods=['POST'])
@requires_auth
def drawcash(user_id):
    user = session.get('user_info')
    account_key = 'account:%s:%s' % (user.get('username'), user_id)
    account_info = json.loads(r_session.get(account_key).decode("utf-8"))

    session_id = account_info.get('session_id')
    user_id = account_info.get('user_id')

    cookies = dict(sessionid=session_id, userid=str(user_id))
    from api import exec_draw_cash
    r = exec_draw_cash(cookies)
    if r.get('r') != 0:
        session['error_message'] = r.get('rd')
        return redirect(url_for('excavators'))
    else:
        session['info_message'] = r.get('rd')
    account_data_key = account_key+':data'
    account_data_value = json.loads(r_session.get(account_data_key).decode("utf-8"))
    account_data_value.get('income')['r_can_use'] = 0
    r_session.set(account_data_key, json.dumps(account_data_value))

    return redirect(url_for('excavators'))


@app.route('/reboot_device/<session_id>', methods=['POST'])
@requires_auth
def reboot_device(session_id):
    setting_url = request.values.get('url')

    s_u = urlparse(setting_url)

    url = "http://kjapi.peiluyou.com:5171/ubus_cd?%s&action=reboot" % s_u.query.replace('user_id','account_id')
    data={"jsonrpc":"2.0","id":1,"method":"call","params":["%s" % session_id,"mnt","reboot",{}]}

    body = dict(data=json.dumps(data), action='onResponse%d' % int(time.time()*1000))
    r = requests.post(url,data=body)

    return redirect(url_for('excavators'))
