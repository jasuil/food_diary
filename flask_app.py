from flask import Flask, redirect
from flask import render_template, request, make_response
from sqlalchemy import text
from datetime import datetime, timezone, timedelta

import table.Model as DB

app = Flask(__name__)
app.config.from_pyfile("config.py")

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get('DB_URL')
# initialize the app with the extension
DB.db.init_app(app)

with app.app_context():
    DB.db.create_all()

def session_proc(session_cookie = None):
    session_value = request.cookies.get('my-session') if session_cookie is None else session_cookie

    if session_value is None:
        return render_template('login.html')

    session_value_arr = session_value.split('-')
    if len(session_value_arr) < 2:
        return render_template('login.html')

    session_info = DB.db.session.execute(text("""select user_id, expire_at
    from  user_session
    where user_id=:user_id and cookie_value=:cookie_value and expire_at >= now()""")
                                         , {'user_id': session_value_arr[0], 'cookie_value': session_value})\
        .fetchone()
    if session_info is None:
        return render_template('login.html')

@app.route("/")
def hello():
    session_info = request.args.get('my-session')
    session_cookie = None
    if session_info is not None and len(session_info.split('-')) == 2:
        res = make_response(render_template('index.html'))
        res.set_cookie(key='my-session', value=session_info, expires=str(datetime.fromtimestamp(int(session_info.split('-')[1]))))
        return res

    login_template = session_proc(session_cookie)
    if login_template is not None:
        return login_template
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id', '')
        pw = data.get('pw', '')

        if user_id == '' or pw == '':
            raise Exception('invalid param error')

        res = make_response()
        user = DB.db.session.execute(text("""
        select * from user where user_id=:user_id and pw=:pw
        """), {'user_id': user_id, 'pw': pw}).fetchone()

        if user is None:
            raise Exception('invalid user')

        expire = int(datetime.fromisoformat(datetime.now(timezone(offset=timedelta(hours=9), name='Asia/Seoul')).isoformat(timespec='seconds')).timestamp() + 6000)
        cookie_value = user.user_id + '-' + str(expire)
        res.set_cookie(key='my-session', value=cookie_value, expires=expire)
        DB.db.session.execute(text("""
        insert into user_session (user_id, cookie_value, create_at, expire_at) values(:user_id, :cookie_value, now(), :expire)
        on duplicate key update
        expire_at=:expire,
        cookie_value=:cookie_value
        """), {'user_id': user_id, 'cookie_value': cookie_value, 'expire': str(datetime.fromtimestamp(expire))})
        DB.db.session.commit()

        return redirect('/?my-session='+cookie_value, 301)
    else:
        return render_template('login.html')


@app.route("/info")
def info():
    login_template = session_proc()
    if login_template is not None:
        return login_template
    user = DB.db.session.execute(text("""
    select * from user
    """))
    list = []
    for u in user:
        list.append(u.user_name + str(u.create_at))
    return ''.join(list)


if __name__ == '__main__':
    app.run()
