__author__ = 'powergx'
from util import hash_password
import json

from flask import Response, request, session, redirect, url_for
from functools import wraps


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    hashed_password = hash_password(password)
    from XunleiCrystal import r_session

    user_info = r_session.get('%s:%s' % ('user', username))
    if user_info is None:
        return False

    user = json.loads(user_info)
    if user.password != hashed_password:
        return False

    return True


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != 'powergx' or not check_auth(auth.username, auth.password) :
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_info') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated