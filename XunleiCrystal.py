from flask import Flask
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    """
    https://red.xunlei.com/?r=usr/queryGift HTTP/1.1
    https://red.xunlei.com/?r=usr/hand&actid=2021&hand=0&v=0&ver=1 HTTP/1.1
    https://red.xunlei.com/?r=mine/info HTTP/1.1
    https://red.xunlei.com/?r=mine/devices_stat HTTP/1.1
    https://red.xunlei.com/?r=mine/ability HTTP/1.1
    https://red.xunlei.com/?r=mine/speed_stat HTTP/1.1
    https://red.xunlei.com/?r=sys/msg HTTP/1.1
    https://red.xunlei.com/?r=usr/reportPlayTime HTTP/1.1
    https://red.xunlei.com/?r=usr/assetio HTTP/1.1


    """
    cookies = dict(sessionid='C3F6EA0EA3E1A7908109D012F71D458B',userid='266244981')
    headers = {'User-Agent': 'RedCrystal/1.4.0 (iPhone; iOS 8.3; Scale/2.00)'}
    s = requests.Session()
    r = s.get('https://red.xunlei.com/?r=mine/info', cookies=cookies,headers=headers)
    print(r.text)

    print(s.get('https://red.xunlei.com/?r=mine/devices_stat', cookies=cookies,headers=headers).text)
    return r.text


if __name__ == '__main__':
    app.run()
