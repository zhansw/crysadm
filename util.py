__author__ = 'powergx'
import hashlib


def hash_password(pwd):
    """
        :param pwd: input password
        :return: return hash md5 password
        """
    from XunleiCrystal import app

    return hashlib.md5(str("%s%s" % (app.config.get("PASSWORD_PREFIX"), pwd)).encode('utf-8')).hexdigest()


def md5(s):
    import hashlib

    return hashlib.md5(s.encode('utf-8')).hexdigest().lower()
