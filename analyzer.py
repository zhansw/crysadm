__author__ = 'powergx'
from flask import render_template, session
from crysadm import app, r_session
from auth import requires_auth
from datetime import datetime, timedelta
import json


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


@app.route('/analyzer')
@requires_auth
def analyzer():
    user = session.get('user_info')
    username = user.get('username')

    user_key = 'user:%s' % username
    str_today = datetime.now().strftime('%Y-%m-%d')
    key = 'user_data:%s:%s' % (username, str_today)

    b_data = r_session.get(key)
    if b_data is None:
        return render_template('analyzer.html', speed_stat_chart=dict(category=[], value=[]))


    today_data = json.loads(b_data.decode('utf-8'))
    print(today_data)
    speed_stat_chart = __get_speed_stat_chart_data(today_data.get('speed_stat'))

    return render_template('analyzer.html', speed_stat_chart=speed_stat_chart)

