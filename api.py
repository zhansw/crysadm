__author__ = 'powergx'
import json
import requests


requests.packages.urllib3.disable_warnings()

def exec_draw_cash(cookies):
    r = get_drawcash_info(cookies)
    if r.get('r') != 0:
        return r
    """
    可以提现就提，不然返回错误信息。
    """
    r = get_balance_info(cookies)
    if r.get('r') != 0:
        return r
    wc_pkg = r.get('wc_pkg')
    if wc_pkg > 200:
        wc_pkg = 200

    r = draw_cash(cookies, wc_pkg)
    if r.get('r') != 0:
        return r

    return r


def draw_cash(cookies,m):
    """
    提现
    :param cookies:
    :return:
    """
    if len(cookies.get('sessionid')) == 128:
        if cookies.get('origin') is not None:
            del cookies['origin']
    else:
        cookies['origin'] = '2'

    body = dict(hand='0',m=str(m),v='3',ver='1')
    r = requests.post('https://red.xunlei.com/?r=usr/drawpkg',data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_drawcash_info(cookies):
    """
    是否可以提现
    {"r":0,"rd":"ok","is_tm":1,"is_bd":1,"tm_tip":"\u63d0\u73b0\u5f00\u653e\u65f6\u95f4\u4e3a\u6bcf\u5468\u4e8c11:00-18:00(\u56fd\u5bb6\u6cd5\u5b9a\u8282\u5047\u65e5\u9664\u5916)","draw_flag":1}
    :param cookies:
    :return:
    """
    if len(cookies.get('sessionid')) == 128:
        if cookies.get('origin') is not None:
            del cookies['origin']
    else:
        cookies['origin'] = '2'

    body = dict(hand='0',v='1',ver='1')
    r = requests.post('https://red.xunlei.com/?r=usr/drawcashInfo', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)


def get_balance_info(cookies):
    "获取余额"
    if len(cookies.get('sessionid')) == 128:
        if cookies.get('origin') is not None:
            del cookies['origin']
    else:
        cookies['origin'] = '2'

    body = dict(hand='0',v='2',ver='1')
    r = requests.post('https://red.xunlei.com/?r=usr/asset', data=body, verify=False, cookies=cookies)
    return json.loads(r.text)