__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app, r_session
from auth import requires_admin, requires_auth
import json
from util import md5
from login import login
from datetime import datetime


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

    print(accounts)
    return render_template('excavators.html', err_msg=err_msg, accounts=accounts)
