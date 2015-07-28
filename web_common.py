__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from crysadm import app, r_session
from auth import requires_admin, requires_auth
from datetime import datetime, timedelta
import json


def __get_yesterday_pdc(username):
    today = datetime.now()
    month_start_date = datetime(year=today.year, month=today.month, day=1).date()
    week_start_date = (today + timedelta(days=-today.weekday())).date()
    begin_date = month_start_date if month_start_date < week_start_date else week_start_date
    begin_date = begin_date + timedelta(days=-1)

    yesterday_m_pdc = 0
    yesterday_w_pdc = 0

    while begin_date < today.date():
        begin_date = begin_date + timedelta(days=1)

        key = 'user_data:%s:%s' % (username, begin_date.strftime('%Y-%m-%d'))

        b_data = r_session.get(key)
        if b_data is None:
            continue

        history_data = json.loads(b_data.decode('utf-8'))
        if begin_date >= month_start_date:
            yesterday_m_pdc += history_data.get('pdc')
        if begin_date >= week_start_date:
            yesterday_w_pdc += history_data.get('pdc')

    return yesterday_m_pdc, yesterday_w_pdc


def __seven_day_pdc(username, history_speed):
    today = datetime.now().date() + timedelta(days=-1)
    begin_date = today + timedelta(days=-7)

    dict_history_speed = dict()
    for speed in history_speed:
        dict_history_speed[speed.get('name')] = int(sum(speed.get('data')) / 24)

    speed_column_value = list()
    category = list()
    value = list()
    while begin_date < today:
        begin_date = begin_date + timedelta(days=1)
        str_date = begin_date.strftime('%Y-%m-%d')
        key = 'user_data:%s:%s' % (username, str_date)
        category.append(str_date)

        if str_date in dict_history_speed:
            speed_column_value.append(dict_history_speed.get(str_date))
        else:
            speed_column_value.append(0)

        b_data = r_session.get(key)
        if b_data is None:
            value.append(0)
            continue

        history_data = json.loads(b_data.decode('utf-8'))
        value.append(history_data.get('pdc'))

    series = [{'name': '平均速度', 'yAxis': 1, 'type': 'column', 'data': speed_column_value, 'tooltip': {
        'valueSuffix': ' KByte/s'
    }},

              {'name': '产量', 'type': 'spline', 'data': value}]
    return category, series


def __get_history_speed_data(username):
    today = datetime.now().date() + timedelta(days=-1)
    begin_date = today + timedelta(days=-7)

    value = list()
    while begin_date < today:
        begin_date = begin_date + timedelta(days=1)
        str_date = begin_date.strftime('%Y-%m-%d')
        key = 'user_data:%s:%s' % (username, str_date)

        b_data = r_session.get(key)
        if b_data is None:
            continue
        history_data = json.loads(b_data.decode('utf-8'))

        day_speed = list()
        day_speed.append([0] * 24)
        for account in history_data.get('speed_stat'):
            day_speed.append(account.get('dev_speed'))
            day_speed.append(account.get('pc_speed'))
        value.append(dict(name=str_date, data=[x / 8 for x in [sum(i) for i in zip(*day_speed)]]))

    return value


def __get_speed_stat_chart_data(speed_stat_data):
    now = datetime.now()
    speed_stat_category = list()
    speed_stat_value = list()
    for i in range(-24, 0):
        speed_stat_category.append('%d:00' % (now + timedelta(hours=i + 1)).hour)

    for speed_data in speed_stat_data:
        this_data = dict(name='矿主ID:' + str(speed_data.get('mid')), data=list())
        speed_stat_value.append(this_data)

        dev_speed = speed_data.get('dev_speed')
        pc_speed = speed_data.get('pc_speed')

        for i in range(0, 24):
            this_data.get('data').append((dev_speed[i] + pc_speed[i]) / 8)

    return dict(category=speed_stat_category, value=speed_stat_value)


def __get_speed_comparison_data(history_data, today_data, str_updated_time):
    category = list()

    value = list()

    value += history_data if len(history_data) < 7 else history_data[-6:]
    for i in range(1, 25):
        if i == 24:
            i = 0
        category.append('%d:00' % i)

    updated_time = datetime.strptime(str_updated_time, '%Y-%m-%d %H:%M:%S')
    if updated_time.date() == datetime.today().date() and updated_time.hour != 0:
        day_speed = list()
        for account in today_data:
            day_speed.append(account.get('dev_speed'))
            day_speed.append(account.get('pc_speed'))

        total_speed = [x / 8 for x in [sum(i) for i in zip(*day_speed)]][0 - updated_time.hour:]
        value.append(dict(name='今天', data=total_speed))

    return dict(category=category, value=value)


@app.route('/dashboard')
@requires_auth
def dashboard():
    user = session.get('user_info')
    username = user.get('username')
    str_today = datetime.now().strftime('%Y-%m-%d')
    key = 'user_data:%s:%s' % (username, str_today)

    b_data = r_session.get(key)
    if b_data is None:
        empty_data = {
            'speed_stat_chart': {
                'category': [],
                'value': []
            },
            'history_speed': {
                'category': [],
                'value': []
            },
            'updated_time': '2015-01-01 00:00:00',
            'm_pdc': 0,
            'last_speed': 0,
            'w_pdc': 0,
            'yesterday_m_pdc': 0,
            'speed_stat': [],
            'yesterday_w_pdc': 0,
            'pdc': 0,
            'balance': 0,
            'seven_days_chart': {
                'category': [],
                'value': []
            }
        }
        return render_template('dashboard.html', today_data=empty_data)

    today_data = json.loads(b_data.decode('utf-8'))
    need_save = False
    if today_data.get('yesterday_m_pdc') is None or today_data.get('yesterday_w_pdc') is None:
        yesterday_m_pdc, yesterday_w_pdc = __get_yesterday_pdc(username)
        today_data['yesterday_m_pdc'] = yesterday_m_pdc
        today_data['yesterday_w_pdc'] = yesterday_w_pdc
        need_save = True

    today_data['m_pdc'] = today_data.get('yesterday_m_pdc') + today_data.get('pdc')
    today_data['w_pdc'] = today_data.get('yesterday_w_pdc') + today_data.get('pdc')

    if today_data.get('history_speed') is None:
        today_data['history_speed'] = __get_history_speed_data(username)
        need_save = True

    if today_data.get('seven_days_chart') is None:
        category, value = __seven_day_pdc(username, today_data.get('history_speed'))
        today_data['seven_days_chart'] = dict(category=category, value=value)
        need_save = True

    if need_save:
        r_session.set(key, json.dumps(today_data))

    today_data['speed_stat_chart'] = __get_speed_stat_chart_data(today_data.get('speed_stat'))
    speed_comparison_data = __get_speed_comparison_data(today_data.get('history_speed'), today_data.get('speed_stat'),
                                                        today_data.get('updated_time'))

    return render_template('dashboard.html', today_data=today_data, speed_comparison_data=speed_comparison_data)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/install')
def install():
    import random, uuid
    from util import hash_password

    if r_session.scard('users') == 0:
        _chars = "0123456789ABCDEF"
        username = ''.join(random.sample(_chars, 6))
        password = ''.join(random.sample(_chars, 6))

        user = dict(username=username, password=hash_password(password), id=str(uuid.uuid1()),
                    active=True, is_admin=True, max_account_no=2, refresh_interval=30,
                    created_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        r_session.set('%s:%s' % ('user', username), json.dumps(user))
        r_session.sadd('users', username)
        return 'username:%s,password:%s' % (username, password)

    return redirect(url_for('login'))


@app.route('/none_user')
@requires_admin
def none_user():
    none_xlAcct = list()
    none_active_xlAcct = list()
    for b_user in r_session.smembers('users'):
        username = b_user.decode('utf-8')

        if r_session.smembers('accounts:' + username) is None or len(r_session.smembers('accounts:' + username)) == 0:
            none_xlAcct.append(username)
        has_active_account = False
        for b_xl_account in r_session.smembers('accounts:' + username):
            xl_account = b_xl_account.decode('utf-8')
            account = json.loads(r_session.get('account:%s:%s' % (username, xl_account)).decode('utf-8'))
            if account.get('active'):
                has_active_account = True
                break
        if not has_active_account:
            none_active_xlAcct.append(username)

    return json.dumps(dict(none_xlAcct=none_xlAcct, none_active_xlAcct=none_active_xlAcct))


@app.context_processor
def add_function():
    def convert_to_yuan(crystal_values):
        if crystal_values >= 10000:
            return str(int(crystal_values / 1000) / 10) + '元'
        return str(crystal_values)

    return dict(convert_to_yuan=convert_to_yuan)


@app.context_processor
def message_box():
    if session is None or session.get('user_info') is None:
        return dict()
    user = session.get('user_info')

    msgs_key = 'user_massages:%s' % user.get('username')

    msg_box = list()
    for b_msg_id in r_session.lrange(msgs_key, 0, -1):
        msg_id = b_msg_id.decode('utf-8')
        b_msg = r_session.get(msg_id)
        if b_msg is None:
            r_session.lrem(msgs_key,msg_id)
            continue

        msg = json.loads(b_msg.decode('utf-8'))
        if msg.get('is_read'):
            continue

        msg_box.append(msg)
        if len(msg_box) > 3:
            break

    return dict(msg_box=msg_box)
