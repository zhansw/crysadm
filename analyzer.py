__author__ = 'powergx'
from flask import render_template, session, Response
from crysadm import app, r_session
from auth import requires_auth
from datetime import datetime, timedelta
import time
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


@app.route('/analyzer/last_30_day')
@requires_auth
def analyzer_last_30_day():
    user = session.get('user_info')
    username = user.get('username')

    value = []
    today = datetime.today()
    for b_data in r_session.mget(
            *['user_data:%s:%s' % (username, (today+timedelta(days=i)).strftime('%Y-%m-%d')) for i in range(-31, 0)]):
        if b_data is None:
            continue
        data = json.loads(b_data.decode('utf-8'))
        update_date = datetime.strptime(data.get('updated_time')[0:10], '%Y-%m-%d')

        value.append([int(time.mktime(update_date.timetuple())*1000), data.get('pdc')])

    return Response(json.dumps(dict(value=value)), mimetype='application/json')


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

    speed_stat_chart = __get_speed_stat_chart_data(today_data.get('speed_stat'))

    return render_template('analyzer.html',
                           speed_stat_chart=speed_stat_chart)

