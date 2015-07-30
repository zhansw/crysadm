__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from crysadm import app, r_session
from auth import requires_admin, requires_auth
from datetime import datetime, timedelta
import util
import json
import uuid




@app.route('/messagebox')
@requires_auth
def messagebox():
    user = session.get('user_info')
    err_msg = util.get_message()

    msgs_key = 'user_messages:%s' % user.get('username')

    msg_box = list()
    for b_msg_id in r_session.lrange(msgs_key, 0, -1):
        msg_id = b_msg_id.decode('utf-8')
        b_msg = r_session.get(msg_id)
        if b_msg is None:
            r_session.lrem(msgs_key,msg_id)
            continue

        msg = json.loads(b_msg.decode('utf-8'))

        msg_box.append(msg)

    return render_template('messages.html', err_msg=err_msg, messages=msg_box)


@app.route('/message/mark_read/<msg_id>')
@requires_auth
def message_mark_read(msg_id):
    user = session.get('user_info')

    msgs_key = 'user_messages:%s' % user.get('username')

    if bytes(msg_id,'utf-8') not in r_session.lrange(msgs_key, 0, -1):
        util.set_message('没有权限修改')
        return redirect(url_for('accounts'))

    msg_key = 'user_message:%s' % msg_id

    msg = json.loads(r_session.get(msg_key).decode('utf-8'))
    msg['is_read'] = True
    r_session.set(msg_key,json.dumps(msg))

    return redirect(url_for('messagebox'))



@app.route('/message/mark_all_read/')
@requires_auth
def mark_all_read():
    user = session.get('user_info')

    msgs_key = 'user_messages:%s' % user.get('username')

    for b_msg_id in r_session.lrange(msgs_key, 0, -1):
        msg_id = b_msg_id.decode('utf-8')
        msg_key = 'user_message:%s' % msg_id
        msg = json.loads(r_session.get(msg_key).decode('utf-8'))
        msg['is_read'] = True
        r_session.set(msg_key,json.dumps(msg))

    return redirect(url_for('messagebox'))


@app.route('/add_msg')
@requires_admin
def add_msg():
    send_msg('powergx', '水晶提现通知', '账号xxxx 水晶提现成', expire=6000)
    return '发送成功'


def send_msg(username, subject, content, expire=3600 * 24 * 7):
    msgs_key = 'user_messages:%s' % username
    msg_id = str(uuid.uuid1())
    msg = dict(id=msg_id, subject=subject, content=content,
               is_read=False, time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    msg_key = 'user_message:%s' % msg_id
    r_session.set(msg_key, json.dumps(msg))
    r_session.expire(msg_key, expire)
    r_session.lpush(msgs_key, msg_id)
