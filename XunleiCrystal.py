from flask import Flask, request, Response, render_template, session, url_for, redirect
import config, socket, redis, hashlib, json, uuid
from functools import wraps

app = Flask(__name__)
r_session = None

def __hash_password(pwd):
    """
        :param pwd: input password
        :return: return hash md5 password
        """
    return hashlib.md5(str("%s%s" % (app.config.get("PASSWORD_PREFIX"), pwd)).encode('utf-8')).hexdigest()


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    hash_password = __hash_password(password)

    user_info = r_session.get('%s:%s' % ('user', username))
    if user_info is None:
        return False

    user = json.loads(user_info)
    if user.password != hash_password:
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


@app.route('/create_user', methods=['POST'])
@requires_admin
def create_user():
    username = request.values.get('username')
    password = request.values.get('password')

    if r_session.get('%s:%s' % ('user', username)) is not None:
        return '账号已存在'
    user = dict(username=username,password=__hash_password(password),id=str(uuid.uuid1()))
    r_session.set('%s:%s' % ('user', username),json.dumps(user))
    return '创建成功'


@app.route('/del_user', methods=['POST'])
@requires_admin
def del_user():
    username = request.values.get('username')

    if r_session.get('%s:%s' % ('user', username)) is None:
        return '账号不存在'

    r_session.delete('%s:%s' % ('user', username))
    return '删除成功'


@app.route('/user/login', methods=['POST'])
def user_login():
    username = request.values.get('username')
    password = request.values.get('password')

    hash_password = __hash_password(password)
    print('%s:%s' % ('user', username))
    user_info = r_session.get('%s:%s' % ('user', username))
    if user_info is None:
        return '用户不存在'

    user = json.loads(user_info.decode('utf-8'))
    if user.get('password') != hash_password:
        return '密码错误'

    session['user_info'] = user

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/tools/redis')
def tools_redis():
    return str(r_session.keys('*'))

@app.route('/12')
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
    return r_session.get('test')
    cookies = dict(sessionid='C3F6EA0EA3E1A7908109D012F71D458B',userid='266244981')
    headers = {'User-Agent': 'RedCrystal/1.4.0 (iPhone; iOS 8.3; Scale/2.00)'}
    s = requests.Session()

    r = s.get('https://red.xunlei.com/?r=mine/info', cookies=cookies,headers=headers)
    print(r.text)

    print(s.get('https://red.xunlei.com/?r=mine/devices_stat', cookies=cookies,headers=headers).text)



if __name__ == '__main__':

    if socket.gethostname() == 'GXMBP.local':
        app.config.from_object(config.DevelopmentConfig)
    elif socket.gethostname() == 'iZ23bo17lpkZ':
        app.config.from_object(config.ProductionConfig)
    else:
        app.config.from_object(config.TestingConfig)

    redis_conf = app.config.get('REDIS_CONF')
    pool = redis.ConnectionPool(host=redis_conf.host, port=redis_conf.port,db=redis_conf.db)

    r_session = redis.Redis(connection_pool=pool)

    app.run()



