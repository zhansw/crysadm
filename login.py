__author__ = 'powergx'
import requests
import time, re
import random
import json


def current_timestamp():
    return int(time.time() * 1000)


def md5(s):
    import hashlib

    return hashlib.md5(s.encode('utf-8')).hexdigest().lower()


def encypt_password(password):
    if not re.match(r'^[0-9a-f]{32}$', password):
        password = md5(md5(password))
    return password


def StrToInt(str):
    bigInteger = 0

    for char in str:
        bigInteger <<= 8
        bigInteger += ord(char)

    return bigInteger


def pow_mod(x, y, z):
    "Calculate (x ** y) % z efficiently."
    number = 1
    while y:
        if y & 1:
            number = number * x % z
        y >>= 1
        x = x * x % z
    return number


def login(username, password):
    session = requests.session()
    exponent = int("010001", 16)
    modulus = int("D6F1CFBF4D9F70710527E1B1911635460B1FF9AB7C202294D04A6F135A906E90E2398123C234340A3CEA0E5EFDC"
                  "B4BCF7C613A5A52B96F59871D8AB9D240ABD4481CCFD758EC3F2FDD54A1D4D56BFFD5C4A95810A8CA25E87FDC75"
                  "2EFA047DF4710C7D67CA025A2DC3EA59B09A9F2E3A41D4A7EFBB31C738B35FFAAA5C6F4E6F", 16)

    param = '{"cmdID":1,"verifyCode":"","isCompressed":0,"rsaKey":{"n":"D6F1CFBF4D9F70710527E1B1911635460B1FF9AB7C202' \
            '294D04A6F135A906E90E2398123C234340A3CEA0E5EFDCB4BCF7C613A5A52B96F59871D8AB9D240ABD4481CCFD758EC3F2FDD54A' \
            '1D4D56BFFD5C4A95810A8CA25E87FDC752EFA047DF4710C7D67CA025A2DC3EA59B09A9F2E3A41D4A7EFBB31C738B35FFAAA5C6F4' \
            'E6F","e":"010001"},"businessType":61,"passWord":"%s","loginType":0,"platformVersion":1,' \
            '"verifyKey":"","sessionID":"","protocolVersion":100,"userName":"%s","extensionList":"",' \
            '"sequenceNo":10000001,"peerID":"%s","clientVersion":"1.0.0"}'

    hash_password = hex(pow_mod(StrToInt(md5(password)), exponent, modulus))[2:]

    _chars = "0123456789ABCDEF";

    peer_id = ''.join(random.sample(_chars, 16))

    param = param % (hash_password, username, peer_id)
    params = json.loads(param)
    headers = {'user-agent': "android-async-http/1.4.3 (http://loopj.com/android-async-http)"}
    text2 = session.get("https://login.mobile.reg2t.sandai.net/", params=params, headers=headers);


    print(param)


if __name__ == '__main__':
    login('powergx@gmail.com', '123456')