__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app, r_session
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


def __seven_day_pdc(username):
    today = datetime.now().date() + timedelta(days=-1)
    begin_date = today + timedelta(days=-7)

    category = list()
    value = list()
    while begin_date < today:
        begin_date = begin_date + timedelta(days=1)
        str_date = begin_date.strftime('%Y-%m-%d')
        key = 'user_data:%s:%s' % (username, str_date)

        category.append(str_date)

        b_data = r_session.get(key)
        if b_data is None:
            value.append(0)
            continue

        history_data = json.loads(b_data.decode('utf-8'))
        value.append(history_data.get('pdc'))

    return category, [dict(data=value, name='产量'),]


def __get_speed_stat_chart_data(speed_stat_data):

    now = datetime.now()
    speed_stat_category = list()
    speed_stat_value = list()
    for i in range(-24, 0):
        speed_stat_category.append('%d:00' % (now + timedelta(hours=i)).hour)

    for speed_data in speed_stat_data:
        this_data  = dict(name='矿主ID:'+ str(speed_data.get('mid')),data=list())
        speed_stat_value.append(this_data)

        dev_speed = speed_data.get('dev_speed')
        pc_speed = speed_data.get('pc_speed')

        for i in range(0, 24):
            this_data.get('data').append((dev_speed[i] + pc_speed[i])/8)

    return speed_stat_category,speed_stat_value


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
            'm_pdc': 0,
            'last_speed': 0,
            'w_pdc': 0,
            'yesterday_m_pdc': 0,
            'speed_stat': [],
            'yesterday_w_pdc': 0,
            'pdc': 0,
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

    if today_data.get('seven_days_chart') is None:
        category, value = __seven_day_pdc(username)
        today_data['seven_days_chart'] = dict(category=category, value=value)
        need_save = True
    if need_save:
        r_session.set(key, json.dumps(today_data))

    category, value = __get_speed_stat_chart_data(today_data.get('speed_stat'))
    today_data['speed_stat_chart'] = dict(category=category, value=value)
    print(today_data)
    return render_template('dashboard.html', today_data=today_data)


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
        return 'username:%s,password:%s' % (username,password)

    return redirect(url_for('login'))

"""
@app.route('/test')
def test():
    from login import login
    from util import md5

    return "a"
"""