__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from crysadm import app, r_session
from auth import requires_admin, requires_auth
import json
from util import hash_password
import uuid
import re
import random


@app.route('/admin')
@requires_admin
def admin():
    users = list()

    for username in sorted(r_session.smembers('users')):
        b_user = r_session.get('user:%s' % username.decode('utf-8'))
        if b_user is None:
            continue
        users.append(json.loads(b_user.decode('utf-8')))


    return render_template('admin.html', users=users,inv_codes=r_session.smembers('invitation_codes'))


@app.route('/generate/inv_code', methods=['POST'])
@requires_admin
def generate_inv_code():
    _chars = "0123456789ABCDEF"
    r_session.smembers('invitation_codes')

    for i in range(0, 10 - r_session.scard('invitation_codes')):
        r_session.sadd('invitation_codes',''.join(random.sample(_chars, 10)))

    return redirect(url_for('admin'))


@app.route('/admin/login_as/<username>', methods=['POST'])
@requires_admin
def generate_login_as(username):
    user_info = r_session.get('%s:%s' % ('user', username))

    user = json.loads(user_info.decode('utf-8'))

    session['admin_user_info'] = session.get('user_info')
    session['user_info'] = user

    return redirect(url_for('dashboard'))


@app.route('/admin_user/<username>')
@requires_admin
def admin_user(username):
    err_msg = None
    if session.get('error_message') is not None:
        err_msg = session.get('error_message')
        session['error_message'] = None

    user = json.loads(r_session.get('user:%s' % username).decode('utf-8'))

    return render_template('user_management.html', user=user, err_msg=err_msg)


@app.route('/admin/change_password/<username>', methods=['POST'])
@requires_admin
def admin_change_password(username):
    n_password = request.values.get('new_password')

    r = r"(?!^[0-9]*$)(?!^[a-zA-Z]*$)^([a-zA-Z0-9]{6,15})$"

    if re.match(r, n_password) is None:
        session['error_message'] = '密码太弱了(6~15位数字加字母).'
        return redirect(url_for(endpoint='admin_user', username=username))

    user_key = '%s:%s' % ('user', username)
    user_info = json.loads(r_session.get(user_key).decode('utf-8'))

    user_info['password'] = hash_password(n_password)
    r_session.set(user_key, json.dumps(user_info))

    return redirect(url_for(endpoint='admin_user', username=username))


@app.route('/admin/change_property/<field>/<value>/<username>', methods=['POST'])
@requires_admin
def admin_change_property(field, value, username):
    user_key = '%s:%s' % ('user', username)
    user_info = json.loads(r_session.get(user_key).decode('utf-8'))

    if field == 'is_admin':
        user_info['is_admin'] = True if value == '1' else False
    elif field == 'active':
        user_info['active'] = True if value == '1' else False
    elif field == 'auto_collect':
        user_info['auto_collect'] = True if value == '1' else False


    r_session.set(user_key, json.dumps(user_info))

    return redirect(url_for(endpoint='admin_user', username=username))


@app.route('/admin/change_user_info/<username>', methods=['POST'])
@requires_admin
def admin_change_user_info(username):
    max_account_no = request.values.get('max_account_no')
    refresh_interval = request.values.get('refresh_interval')

    r = r"^[1-9]\d*$"

    if re.match(r, refresh_interval) is None:
        session['error_message'] = '刷新时间必须为整数.'
        return redirect(url_for(endpoint='admin_user', username=username))

    if re.match(r, max_account_no) is None:
        session['error_message'] = '迅雷账号限制必须为整数.'
        return redirect(url_for(endpoint='admin_user', username=username))

    if not 4 < int(refresh_interval) < 61:
        session['error_message'] = '迅雷账号限制必须为 5~60 秒.'
        return redirect(url_for(endpoint='admin_user', username=username))

    if not 0 < int(max_account_no) < 21:
        session['error_message'] = '迅雷账号限制必须为 1~20.'
        return redirect(url_for(endpoint='admin_user', username=username))

    user_key = '%s:%s' % ('user', username)
    user_info = json.loads(r_session.get(user_key).decode('utf-8'))

    user_info['max_account_no'] = int(max_account_no)
    user_info['refresh_interval'] = int(refresh_interval)

    r_session.set(user_key, json.dumps(user_info))

    return redirect(url_for(endpoint='admin_user', username=username))


@app.route('/admin/del_user/<username>', methods=['GET'])
@requires_admin
def admin_del_user(username):
    if r_session.get('%s:%s' % ('user', username)) is None:
        session['error_message'] = '账号不存在'
        return redirect(url_for(endpoint='admin_user', username=username))

    # do del user
    r_session.delete('%s:%s' % ('user', username))
    r_session.srem('users', username)
    for b_account_id in r_session.smembers('accounts:' + username):
        account_id = b_account_id.decode('utf-8')
        r_session.delete('account:%s:%s' % (username, account_id))
        r_session.delete('account:%s:%s:data' % (username, account_id))
    r_session.delete('accounts:' + username)

    for key in r_session.keys('user_data:%s:*' % username):
        r_session.delete(key.decode('utf-8'))

    return redirect(url_for('admin'))
