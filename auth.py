__author__ = 'powergx'
from util import hash_password
import json

from flask import Response, request, session, redirect, url_for
from functools import wraps


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_info') is None:
            return redirect(url_for('login'))
        if session.get('user_info').get('is_admin') is None or not session.get('user_info').get('is_admin'):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_info') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated
