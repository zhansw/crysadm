__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app, r_session
from auth import requires_admin, requires_auth
import json
from util import md5
from login import login
from datetime import datetime


@app.route('/accounts')
@requires_auth
def accounts():
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

    print(accounts)
    return render_template('accounts.html', err_msg=err_msg, accounts=accounts)


@app.route('/account/add', methods=['POST'])
@requires_auth
def account_add():
    account_name = request.values.get('xl_username')
    password = request.values.get('xl_password')
    md5_password = md5(password)

    user = session.get('user_info')

    accounts_key = 'accounts:%s' % user.get('username')
    account_set = r_session.smembers(accounts_key)
    if account_set is not None and account_name in account_set:
        session['error_message'] = '该账号已经存在。'
        return redirect(url_for('accounts'))

    login_result = login(account_name, md5_password)
    if login_result.get('errorCode') != 0:
        error_message = login_result.get('errorDesc')
        session['error_message'] = '登陆失败，错误信息：%s。' % error_message
        return redirect(url_for('accounts'))

    xl_session_id = login_result.get('sessionID')
    xl_nick_name = login_result.get('nickName')
    xl_user_name = login_result.get('userName')
    xl_user_id = login_result.get('userID')
    xl_user_new_no = login_result.get('userNewNo')
    xl_account_name = account_name
    xl_password = md5_password

    r_session.sadd(accounts_key, xl_account_name)

    account_key = 'account:%s:%s' % (user.get('username'), xl_account_name)
    xl_account_data = dict(session_id=xl_session_id, nick_name=xl_nick_name, username=xl_user_name,
                           user_id=xl_user_id, user_new_no=xl_user_new_no, account_name=xl_account_name,
                           password=xl_password, active=True, status='' ,
                           createdtime=datetime.now().strftime('%Y-%m-%d %H:%M'))
    r_session.set(account_key, json.dumps(xl_account_data))

    return redirect(url_for('accounts'))

@app.route('/account/del/<xl_id>', methods=['POST'])
@requires_auth
def account_del(xl_id):
    user = session.get('user_info')
    accounts_key = 'accounts:%s' % user.get('username')
    account_key = 'account:%s:%s' % (user.get('username'), xl_id)
