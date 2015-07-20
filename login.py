__author__ = 'powergx'
import requests
import random
import json


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


def login(username, md5_password):
    exponent = int("010001", 16)
    modulus = int("D6F1CFBF4D9F70710527E1B1911635460B1FF9AB7C202294D04A6F135A906E90E2398123C234340A3CEA0E5EFDC"
                  "B4BCF7C613A5A52B96F59871D8AB9D240ABD4481CCFD758EC3F2FDD54A1D4D56BFFD5C4A95810A8CA25E87FDC75"
                  "2EFA047DF4710C7D67CA025A2DC3EA59B09A9F2E3A41D4A7EFBB31C738B35FFAAA5C6F4E6F", 16)

    param = '{"cmdID":1,"isCompressed":0,"rsaKey":{"n":"D6F1CFBF4D9F70710527E1B1911635460B1FF9AB7C202' \
            '294D04A6F135A906E90E2398123C234340A3CEA0E5EFDCB4BCF7C613A5A52B96F59871D8AB9D240ABD4481CCFD758EC3F2FDD54A' \
            '1D4D56BFFD5C4A95810A8CA25E87FDC752EFA047DF4710C7D67CA025A2DC3EA59B09A9F2E3A41D4A7EFBB31C738B35FFAAA5C6F4' \
            'E6F","e":"010001"},"businessType":61,"passWord":"%s","loginType":0,"platformVersion":1,' \
            '"verifyKey":"","sessionID":"","protocolVersion":101,"userName":"%s","extensionList":"",' \
            '"sequenceNo":10000015,"peerID":"%s","clientVersion":"1.0.0","appName":"ANDROID-com.xunlei.redcrystalandroid"}'

    hash_password = hex(pow_mod(StrToInt(md5_password), exponent, modulus))[2:].upper()

    _chars = "0123456789ABCDEF"

    peer_id = ''.join(random.sample(_chars, 16))

    param = param % (hash_password, username, peer_id)

    headers = {'user-agent': "RedCrystal/1.5.0 (iPhone; iOS 8.4; Scale/2.00)"}
    r = requests.post("https://login.mobile.reg2t.sandai.net/", data=param, headers=headers, verify=False)

    login_status = json.loads(r.text)
    return login_status
