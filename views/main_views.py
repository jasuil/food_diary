from flask import Blueprint
from flask import render_template, request, make_response
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
from dto.SessionInfo import SessionInfo
import service.mail_sender as mail_sender
import table.Model as DB
import json
import uuid

bp = Blueprint('main', __name__, url_prefix='/')

@bp.before_app_request
def session_proc():
    if request.path != '/login':
        session_value = request.cookies.get('my-session')
        session_info = SessionInfo()
        if session_value is None:
            return render_template('login.html')

        session_value_arr = session_value.split('-')
        if len(session_value_arr) < 2:
            return render_template('login.html')

        user_session = DB.db.session.execute(text("""select user_id, expire_at
        from  user_session
        where user_id=:user_id and cookie_value=:cookie_value and expire_at >= now()""")
                                             , {'user_id': session_value_arr[0], 'cookie_value': session_value}) \
            .fetchone()
        if user_session is None:
            return render_template('login.html')

        session_info.user_id = user_session.user_id


@bp.route("/")
def hello():
    return render_template('index.html')


@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id', '')
        pw = data.get('pw', '')

        if user_id == '' or pw == '':
            raise Exception('invalid param error')

        res = make_response({'result': 'ok'})
        user = DB.db.session.execute(text("""
        select * from user where user_id=:user_id and pw=:pw
        """), {'user_id': user_id, 'pw': pw}).fetchone()

        if user is None:
            raise Exception('invalid user')

        expire = int(datetime.fromisoformat(
            datetime.now(timezone(offset=timedelta(hours=9), name='Asia/Seoul')).isoformat(
                timespec='seconds')).timestamp() + 6000)
        cookie_value = user.user_id + '-' + str(expire)
        res.set_cookie(key='my-session', value=cookie_value, expires=expire)
        DB.db.session.execute(text("""
        insert into user_session (user_id, cookie_value, create_at, expire_at) values(:user_id, :cookie_value, now(), :expire)
        on duplicate key update
        expire_at=:expire,
        cookie_value=:cookie_value
        """), {'user_id': user_id, 'cookie_value': cookie_value, 'expire': str(datetime.fromtimestamp(expire))})
        DB.db.session.commit()
        return res
    else:
        return render_template('login.html')


@bp.route("/user-info")
def info():
    session_value = request.cookies.get('my-session')
    session_value_arr = session_value.split('-')

    user = DB.db.session.execute(text("""
    select * from user
    where user_id=:user_id
    """), {'user_id': session_value_arr[0]}).fetchone()
    return json.dumps({'name': user.user_name, 'create_at': str(user.create_at)})


@bp.route("/<string:user_id>/password", methods=["POST", "GET"])
def password_update(user_id):
    if request.method == 'POST':
        data = request.json
        pw = data.get('pw', '')

        if pw == '':
            raise Exception('invalid pw')
        session = DB.db.session
        user = session.query(DB.User).filter(DB.User.user_id == 'jasuil').one()
        user.pw = pw
        session.commit()
    else:
        session = DB.db.session
        user = session.query(DB.User).filter(DB.User.user_id == 'jasuil').one()
        user.pw = str(uuid.uuid4())
        session.commit()

        mail_sender.mail_api_open()
        mail_sender.gmail_create_draft('food diary password reset',
                                       'your id ' + user.user_id + ' has changed to new pw:' + user.pw,
                                       'jasuil@daum.net')
    return json.dumps({'result': 'ok'})
