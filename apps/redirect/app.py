from flask import Flask, redirect, request, make_response, render_template, url_for, flash
import celery
import psycopg2
from datetime import datetime
import json
import requests
from users import DefaultUser, AdminUser
import flask_login
from os import environ

"""
The redirect app.
References inbound requests against a DB to determine the correct redirect location.
Parameters are forwarded on redirect, however the base URL needs to be resolved.
"""

DEBUG = False
REDIRECT_DB_USERNAME = environ['REDIRECT_DB_USERNAME']
REDIRECT_DB_PASSWORD = environ['REDIRECT_DB_PASSWORD']
SECRET_KEY = environ['SECRET_KEY']
ADMIN_PASSWORD = environ['ADMIN_PASSWORD']

if DEBUG:
    celery_app = celery.Celery('app', broker='amqp://guest:guest@localhost:5672')
    db_host = 'localhost'
else:
    celery_app = celery.Celery('app', broker='amqp://guest:guest@redirect_mq:5672')
    db_host = 'redirect_db'

flask_app = Flask(__name__)
flask_app.secret_key = SECRET_KEY

login_manager = flask_login.LoginManager()
login_manager.init_app(flask_app)


def get_db_connection():
    db_connection = psycopg2.connect("\
            host={host} \
            dbname=clickonly \
            user={user} \
            password={password}".format(host=db_host, user=REDIRECT_DB_USERNAME, password=REDIRECT_DB_PASSWORD))
    return db_connection


@celery.task
def insert_db(location, history: list):
    db_conn = get_db_connection()
    with db_conn:
        with db_conn.cursor() as curs:
            curs.execute("""
                         INSERT INTO public.redirects (id, ts, location, history) VALUES 
                         (%s, %s, %s, %s)
                         """,
                         (insert_db.request.id,
                          int(datetime.utcnow().timestamp()),
                          location,
                          history))
    db_conn.close()


def get_redirect_table():
    db_conn = get_db_connection()
    with db_conn:
        with db_conn.cursor() as curs:
            curs.execute("""
                         SELECT location, redirect 
                         FROM public.location 
                         """)
            redirect_table = dict()
            for record in curs:
                redirect_table[record[0].strip()] = record[1].strip()
    db_conn.close()
    return redirect_table


@flask_app.route('/r/<key>')
def _redirect(key):
    redirect_table = get_redirect_table()
    if key in redirect_table:
        try:
            history = json.loads(request.cookies.get('history', '[]'))
        except json.JSONDecodeError:
            history = []
        history.append(key)
        insert_db.delay(key, history)

        resp = make_response(redirect(redirect_table[key]))
        resp.set_cookie('history', json.dumps(history))
    else:
        resp = make_response(render_template('no_redirect.html', key=key))
    return resp


@flask_app.route('/route/delete/<route>')
@flask_login.login_required
def delete_route(route: str):
    db_conn = get_db_connection()
    with db_conn:
        with db_conn.cursor() as curs:
            curs.execute("""
                         DELETE FROM public.location WHERE location = '{}'
                         """.format(route))
    db_conn.close()
    return redirect(url_for('root'))


def _validate_add_route_form(form: dict):
    if len(form['location']) > 255:
        return False
    r = requests.get(form['redirect'])
    if not r.ok:
        return False
    return True


@flask_app.route('/route/submit', methods=['POST'])
@flask_login.login_required
def submit_route():
    if _validate_add_route_form(request.form):
        db_conn = get_db_connection()
        with db_conn:
            with db_conn.cursor() as curs:
                curs.execute("""
                             INSERT INTO public.location (ts, location, redirect) VALUES 
                             (%s, %s, %s)
                             """,
                             (int(datetime.utcnow().timestamp()),
                              request.form['location'].strip(),
                              request.form['redirect'].strip()))
        db_conn.close()
    return redirect(url_for('root'))


@flask_app.route('/')
def root():
    redirect_table = get_redirect_table()
    return render_template('root.html', to_table=redirect_table)


@login_manager.user_loader
def load_user(user_id):
    if user_id == 0:
        user = AdminUser()
    else:
        user = DefaultUser()
    return user


@flask_app.route('/login')
def login():
    return render_template('login.html')


@flask_app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('root'))


@flask_app.route('/authenticate', methods=['POST'])
def authenticate():
    form = request.form
    if form['password'] == ADMIN_PASSWORD:
        user = AdminUser()
        flask_login.login_user(user, remember=True)
        return redirect(url_for('root'))
    else:
        flash('invalid_password')
        return redirect(url_for('login'))


if __name__ == '__main__':
    flask_app.run('localhost', '8080')
