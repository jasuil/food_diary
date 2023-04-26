
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, jsonify, current_app, make_response
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config.from_pyfile("config.py")

database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
app.database = database

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        res = make_response(render_template('index.html')
)
        user = current_app.database.execute(text("""
        select * from user where id=:id and pw=:pw
        limit 1
        """), {'id':id, 'pw':pw})

        for u in user:
            res.set_cookie('my-session', id)

        return res
    else:
        return render_template('login.html')

@app.route("/info")
def info():
    user = current_app.database.execute(text("""
    select * from user
    """))
    list = []
    for u in user:
        list.append(u.name + str(u.create_at))
    return ''.join(list)

if __name__ == '__main__':
    app.run()
