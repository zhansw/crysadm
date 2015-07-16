__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app,r_session
from auth import requires_admin, requires_auth
import json
from util import hash_password
import uuid


@app.route('/user/login', methods=['POST'])
def user_login():
    username = request.values.get('username')
    password = request.values.get('password')

    hashed_password = hash_password(password)
    print('%s:%s' % ('user', username))
    user_info = r_session.get('%s:%s' % ('user', username))
    if user_info is None:
        return '用户不存在'

    user = json.loads(user_info.decode('utf-8'))
    print(hashed_password)
    print(user.get('password'))
    if user.get('password') != hashed_password:
        return '密码错误'

    session['user_info'] = user

    return redirect(url_for('dashboard'))


@app.route('/user/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))