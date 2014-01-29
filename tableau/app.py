#!/usr/bin/env python

from flask import Flask, render_template, redirect, request, url_for, jsonify
from utils import dbopen
import elasticsearch

app = Flask(__name__)
SIMDB = "/media/mtc/Data/tasktree-data/f3/similar-db/date-2014-01-28-indices-nep-ebl-bsz-size-5-sources-nep-ebl.db"

@app.route("/unrated")
def unrated():
    with dbopen(SIMDB) as cursor:
        cursor.execute("SELECT * from similarity limit 250")
        results = cursor.fetchall()
    return render_template('unrated.html', name='unrated', results=results)

@app.route("/rated")
def rated():
    name = request.args.get('v', 'plus')
    return render_template('index.html', name=name)

@app.route("/summary")
def summary():
    return render_template('index.html', name='summary')

@app.route("/search")
def search():
    return render_template('index.html', name='search')

@app.route("/doc/<index>/<id>")
def doc(index, id):
    es = elasticsearch.Elasticsearch()
    source = es.get_source(index=index, id=id)
    return jsonify(source)

@app.route("/")
def hello():
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
