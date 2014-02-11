#!/usr/bin/env python

from crossdomain import crossdomain
from flask import (Flask, render_template, session, redirect, request, url_for,
                   jsonify, Response, send_from_directory, abort, flash)
from utils import dbopen
from timer import Timer
from operator import itemgetter
import config
import time
import elasticsearch
import json
import os
import random

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yXasdsadR~sdgXHH!jmN]LWX/,?RT'


NAME_SOURCE_ID_MAP = {
    'bsz': 0,
    'nep': 3,
    'ebl': 4,
    'naxos': 5,
    'mor': 6,
    'pao': 7,
    'lfer': 8,
    'ema': 9,
    'mtc': 10,
    'bms': 11,
    'bvb': 12,
    'disson': 13,
    'rism': 14,
    'imslp': 15,
    'elsevier': 16,
    'nl': 17,
    'oso': 18,
    'ksd': 19,
    'bnf': 20,
    'gbv': 21,
    'qucosa': 22,
    'hszigr': 23,
    'ebrary': 24,
    'swbod': 25,
    'doab': 26,
    'doaj': 28,
}

@app.before_request
def ensure_pairs():
    """ Ensure pairs are defined. """
    if not 'pairs' in session or not session['pairs']:
        with dbopen(config.SIM_DB) as cursor:
            cursor.execute("""SELECT DISTINCT i1, i2, count(*)
                              FROM similarity group by i1, i2""")
            results = cursor.fetchall()
            session['pairs'] = [tuple(result[:2]) for result in results]


@app.context_processor
def utility_processor():
    def now():
        return time.time()
    return dict(now=now)


@app.route("/pairs")
def pairs():
    with dbopen(SIM_DB) as cursor:
        cursor.execute("""SELECT distinct i1, i2, count(*)
                          FROM similarity GROUP BY i1, i2""")
        results = cursor.fetchall()
    return Response(json.dumps(results), mimetype="application/json")


@app.route("/summary")
def summary():
    return render_template('index.html', name='summary')


@app.route("/search")
def search():
    return render_template('search.html', name='search')


@app.route("/doc/<index>/<id>")
@crossdomain(origin='*')
def doc(index, id):
    with Timer() as timer:
        es = elasticsearch.Elasticsearch()
        source = es.get_source(index=index, id=id)
    app.logger.debug("ES query: %s" % timer.elapsed_s)
    return jsonify(source)


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        pairs = [tuple(k.split('-')) for k, v in request.form.iteritems() if v == 'on']
        session['pairs'] = pairs
        return redirect(url_for('begin'))

    with dbopen(config.SIM_DB) as cursor:
        cursor.execute("SELECT DISTINCT i1, i2, count(*) from similarity group by i1, i2")
        results = cursor.fetchall()
    return render_template('settings.html', results=results)


@app.route("/begin")
def begin():
    """ Pick an item from the database and redirect to the comparison screen """
    filters = ["""(i1 = '{0}' AND i2 = '{1}')""".format(i1, i2)
               for i1, i2 in session.get('pairs', [])]
    disjunction = " OR ".join(filters)
    where_clause = "WHERE {}".format(disjunction) if disjunction else ""

    with dbopen(config.SIM_DB) as cursor:
        cursor.execute("""SELECT * FROM similarity
                          %s ORDER BY RANDOM() LIMIT 1""" % where_clause)
        result = cursor.fetchone()
    left = "%s:%s" % (result[1], result[2])
    right = "%s:%s" % (result[3], result[4])
    return redirect(url_for('compare', left=left, right=right))

@app.route("/initdb")
def initdb():
    """ Initialize feedback database. """
    with dbopen(config.FEEDBACK_DB) as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS feedback
                          (i1 TEXT, r1 TEXT, i2 TEXT, r2 TEXT,
                            vote TEXT, ip TEXT, started REAL, stopped REAL)""")
    return redirect(url_for('hello'))



@app.route("/compare")
def compare():
    # see if we got feedback
    feedback = request.args.get('feedback')
    if feedback:
        stopped = time.time()

        left, right, vote, started = feedback.split("::", 3)
        leftIndex, leftId = left.split(":", 1)
        rightIndex, rightId = right.split(":", 1)

        with dbopen(config.FEEDBACK_DB) as cursor:
            cursor.execute("""INSERT INTO feedback
                (i1, r1, i2, r2, vote, ip, started, stopped)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?) """,
                (leftIndex, leftId, rightIndex, rightId,
                 vote, request.remote_addr, started, stopped))
        app.logger.debug("wrote feedback for: %s" % request.args)
        flash('Thank you. Your feedback has been recorded.')
        return redirect(url_for('compare', left=request.args.get('left'), right=request.args.get('right')))

    try:
        left, right = itemgetter('left', 'right')(request.args)
        leftIndex, leftId = left.split(":", 1)
        rightIndex, rightId = right.split(":", 1)
    except KeyError as error:
        abort(400)

    # the payload for the current comparison
    payload = {"left": {"index": leftIndex, "id": leftId,
                        "source_id": NAME_SOURCE_ID_MAP.get(leftIndex)},
               "right": {"index": rightIndex, "id": rightId,
                         "source_id": NAME_SOURCE_ID_MAP.get(rightIndex)},
               "base": config.BASE}

    # prefetch next comparison pair
    filters = ["""(i1 = '{0}' AND i2 = '{1}')""".format(i1, i2)
               for i1, i2 in session.get('pairs', [])]
    disjunction = " OR ".join(filters)
    where_clause = "WHERE {}".format(disjunction) if disjunction else ""

    with dbopen(config.SIM_DB) as cursor:
        cursor.execute("""SELECT * FROM similarity
                          %s ORDER BY RANDOM() LIMIT 1""" % where_clause)
        result = cursor.fetchone()
    left = "%s:%s" % (result[1], result[2])
    right = "%s:%s" % (result[3], result[4])
    next_pair = {'left': left, 'right': right}

    return render_template('compare.html', name='compare', payload=payload,
                           next_pair=next_pair)


@app.route("/")
def hello():
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
