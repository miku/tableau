#!/usr/bin/env python

from config import SIMDB
from crossdomain import crossdomain
from flask import Flask, render_template, session, redirect, request, url_for, jsonify, Response, send_from_directory
from utils import dbopen
from timer import Timer
import elasticsearch
import json
import os
import random

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yXasdsadR~sdgXHH!jmN]LWX/,?RT'

@app.route("/pairs")
def pairs():
    with dbopen(SIMDB) as cursor:
        cursor.execute("SELECT distinct i1, i2, count(*) from similarity group by i1, i2")
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
        return redirect(url_for('compare'))

    with dbopen(SIMDB) as cursor:
        cursor.execute("SELECT distinct i1, i2, count(*) from similarity group by i1, i2")
        results = cursor.fetchall()
    return render_template('settings.html', results=results)

@app.route("/compare")
def compare():
    with Timer() as timer:
        if not 'pairs' in session or not session['pairs']:
            with dbopen(SIMDB) as cursor:
                cursor.execute("SELECT distinct i1, i2, count(*) from similarity group by i1, i2")
                results = cursor.fetchall()
                session['pairs'] = [tuple(result[:2]) for result in results]
        # TODO: hello SQLI!
        filters = ["""(i1 = '{0}' AND i2 = '{1}')""".format(i1, i2)
                   for i1, i2 in session.get('pairs', [])]
        disjunction = " OR ".join(filters)
        where_clause = "WHERE {}".format(disjunction) if disjunction else ""

    app.logger.debug("SQL query: %s" % timer.elapsed_s)
    # return render_template('compare.html', name='compare', result=result)
    # return render_template('compare_w_react.html', name='compare', result=result)
    return render_template('example.html', name='compare', result=result)

@app.route("/")
def hello():
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
