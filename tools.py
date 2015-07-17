__author__ = 'powergx'
from flask import request, Response, render_template, session, url_for, redirect
from XunleiCrystal import app, r_session
from auth import requires_admin, requires_auth
import json
from util import hash_password
import uuid


@app.route('/tools/redis')
def tools_redis():
    return str(r_session.keys('*'))
