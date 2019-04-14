from flask import Flask, redirect, request, make_response, render_template
import celery
import psycopg2
from datetime import datetime
import json
from redirect_table import TO
from os import environ

"""
The redirect app.
References inbound requests against a DB to determine the correct redirect location.
Parameters are forwarded on redirect, however the base URL needs to be resolved.
"""

REDIRECT_DB_USERNAME = environ['REDIRECT_DB_USERNAME']
REDIRECT_DB_PASSWORD = environ['REDIRECT_DB_USERNAME']

flask_app = Flask(__name__)
celery_app = celery.Celery('app', broker='amqp://guest:guest@redirect_mq:5672')
# celery_app = celery.Celery('app', broker='amqp://guest:guest@localhost:5672')


@celery.task
def insert_db(location, history: list):
    db_conn = psycopg2.connect("\
        host=redirect_db \
        dbname=clickonly \
        user={user} \
        password={password}".format(user=REDIRECT_DB_USERNAME, password=REDIRECT_DB_PASSWORD))
    cur = db_conn.cursor()

    cur.execute("""
                INSERT INTO public.redirects (id, ts, location, history) VALUES 
                (%s, %s, %s, %s)
                """,
                (insert_db.request.id,
                 int(datetime.utcnow().timestamp()),
                 location,
                 history))
    db_conn.commit()


@flask_app.route('/r/<key>')
def _redirect(key):
    if key in TO:
        try:
            history = json.loads(request.cookies.get('history', '[]'))
        except json.JSONDecodeError:
            history = []
        history.append(key)
        insert_db.delay(key, history)

        resp = make_response(redirect(TO[key]))
        resp.set_cookie('history', json.dumps(history))
    else:
        resp = make_response(render_template('no_redirect.html', key=key))
    return resp


if __name__ == '__main__':
    flask_app.run('localhost', '8080')
