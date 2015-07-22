__author__ = 'powergx'
import requests
import random
import json
from Crypto.PublicKey import RSA
from util import md5
from Crypto.Cipher import PKCS1_OAEP,PKCS1_v1_5
from base64 import b64encode


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


def int2char(n):
    BI_RM = "0123456789abcdefghijklmnopqrstuvwxyz"
    return BI_RM[n]

def b64tohex(s):
    b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    b64padchar = "="
    ret = ""
    k = 0
    slop = None
    for i in range(0,len(s)):
        if s[i]== b64padchar:
            break

        v = b64map.index(s[i])
        if v < 0:
            continue

        if k == 0:
            ret += int2char(v >> 2)
            slop = v & 3
            k = 1
        else:
            if k == 1:
                ret += int2char((slop << 2) | (v >> 4))
                slop = v & 15
                k = 2
            else:
                if k == 2:
                    ret += int2char(slop)
                    ret += int2char(v >> 2)
                    slop = v & 3
                    k = 3
                else:
                    ret += int2char((slop << 2) | (v >> 4))
                    ret += int2char(v & 15)
                    k = 0

    if k == 1:
        ret += int2char(slop << 2)

    return ret


class RSAKey():
    n = None
    e = 0
    d = None
    p = None
    q = None
    dmp1 = None
    dmq1 = None
    coeff = None

    def __init__(self):
        pass


    def SetPublic(self, N, E):
        if N != None and E != None and len(N) > 0 and len(E) > 0:
            self.n = int(N, 16)
            self.e = int(E, 16)
        else:
            print("Invalid RSA public key")
"""
    def pkcs1pad3(self,s, n):
        if n < len(s) + 11:
            print("Message too long for RSA")
            return None

        ba = list()
        i = 0
        j = 0
        lens = len(s)
        while i < lens and j < n:

            c = s[i]
            i+=1
            if c < 128:

                ba[j] = c
                j+=1
            else:
                if (c > 127) and (c < 2048):

                    ba[j] = (c >> 6) | 192
                    j+=1
                    ba[j] = (c & 63) | 128
                    j+=1
                else:

                    ba[j] = (c >> 12) | 224;
                    j+=1
                    ba[j] = ((c >> 6) & 63) | 128;
                    j+=1
                    ba[j] = (c & 63) | 128
                    j+=1



        ba[j] = 0;
        j+=1
        rng = SecureRandom();
        x = list()
        while j < n:
            x[0] = 0;
            while x[0] == 0:
                rng.nextBytes(x)

            ba[j] = x[0]
            j+=1

        return int(ba)


    def RSAEncrypt(self,text):
        m = self.pkcs1pad3(text, (len(self.n) + 7) >> 3)
        if m == None:
            return None

        c = self.doPublic(m)
        if c == None:
            return None

        h = c.toString(16)
        if (len(h) & 1) == 0:
            return h
        else:
            return "0" + str(h)


"""

def new_login(username,password,captcha,check_n,check_e):
    md5_password = md5(password)
    b64_n = b64tohex(check_n)
    b64_e = b64tohex(check_e)

    RSAkey = RSA.construct((int(b64_n, 16),int(b64_e, 16)))
    RSAkey = RSA.generate(1024)
    cipher = PKCS1_v1_5.new(RSAkey)
    b = b64encode(cipher.encrypt((md5_password+captcha.upper()).encode('utf-8')))
    a = RSAkey.encrypt((md5_password+captcha.upper()).encode('utf-8'),0)
    t = RSAKey()
    t.SetPublic(b64tohex(check_n), b64tohex(check_e))

    print(b64_n,b64_e)