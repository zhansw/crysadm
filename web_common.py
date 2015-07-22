__author__ = 'powergx'
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
        speed_stat_category.append('   %s' % (now + timedelta(hours=i)).strftime('%H'))

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
        pass

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
        print(category, value)
    if need_save:
        r_session.set(key, json.dumps(today_data))

    category, value = __get_speed_stat_chart_data(today_data.get('speed_stat'))
    today_data['speed_stat_chart'] = dict(category=category, value=value)

    return render_template('dashboard.html', today_data=today_data)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/12')
def hello_world():
    from login import new_login
    new_login('powergx@gmail.com','021415','!Gdt',
              'ojx/c8S645rVboX1LNLZyFrRze18YlpFCzh4rxTwS2N7yTALd6+SIewRa4p26y2TA4OXvOZf29E9k1onzu95E8qWXxfQs0lI5e6Y+As7qw0/52Iw+8YabQhYxyFALLRdwZZ9R//L9W8XXejTPKRhmxZz9JRrwlCFfioGfDjkyzjS/Fu531puZHdFi7G1gSKxbp7V0L7YL+0iSQOrPyeC5c7eivOsLzq/kv9yKtF7PtNK0QWAKfum8HtqhBuI4y7CwuqRebhzl6Z5cZWJg8hsqgEeMHvvIaxUROzROSGMiJzvCt7Ms7DxY4rOPdyCFb1hBvl5L7CCafguOvJ0fovI5w==',
              'AQAB')
    return ''
