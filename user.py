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
        session['error_message'] = '用户不存在'
        return redirect(url_for('login'))

    user = json.loads(user_info.decode('utf-8'))

    if user.get('password') != hashed_password:
        session['error_message'] = '密码错误'
        return redirect(url_for('login'))

    session['user_info'] = user

    return redirect(url_for('dashboard'))


@app.route('/login')
def login():
    if session.get('user_info') is not None:
        return redirect(url_for('dashboard'))

    err_msg = None
    if session.get('error_message') is not None:
        err_msg = session.get('error_message')
        session['error_message'] = None

    return render_template('login.html', err_msg=err_msg)


@app.route('/user/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/tools/create_user', methods=['POST'])
@requires_admin
def create_user():
    username = request.values.get('username')
    password = request.values.get('password')

    if r_session.get('%s:%s' % ('user', username)) is not None:
        return '账号已存在'
    user = dict(username=username, password=hash_password(password), id=str(uuid.uuid1()))
    r_session.set('%s:%s' % ('user', username), json.dumps(user))
    r_session.sadd('users', username)
    return '创建成功'


@app.route('/tools/del_user', methods=['POST'])
@requires_admin
def del_user():
    username = request.values.get('username')

    if r_session.get('%s:%s' % ('user', username)) is None:
        return '账号不存在'

    r_session.delete('%s:%s' % ('user', username))
    r_session.srem('users', username)
    return '删除成功'
