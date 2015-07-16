__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app, r_session
from auth import requires_admin, requires_auth
import json
from util import hash_password
import uuid


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


@app.route('/tools/redis')
def tools_redis():
    return str(r_session.keys('*'))
