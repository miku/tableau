#!/usr/bin/env python

from flask import Flask, render_template, redirect, request, url_for
from utils import dbopen
import jsonpath_rw as jpath
import elasticsearch
app = Flask(__name__)

SIMDB = "/media/mtc/Data/tasktree-data/f3/similar-db/date-2014-01-28-indices-nep-ebl-bsz-size-5-sources-nep-ebl.db"
x245a = jpath.parse("content['245'][*].a")
# x245a = jpath.parse("content['245'][0].a")
# x245a = jpath.parse("content['245'][0].c")

x300a = jpath.parse("content['300'][0].a")
# authors
x100a = jpath.parse("content.['100'][0].a")
x700a = jpath.parse("content.['700'][0].a")


def xauthors(source=None):
    vals = ([match.value for match in x100a.find(source)] +
            [match.value for match in x700a.find(source)])
    return ' '.join(vals).strip().encode('utf-8')


@app.route("/unrated")
def unrated():
    with dbopen(SIMDB) as cursor:
        cursor.execute("SELECT * from similarity limit 500")
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

@app.route("/title/<index>/<id>")
def title(index, id):
    es = elasticsearch.Elasticsearch()
    source = es.get_source(index=index, id=id)
    vals = (match.value for match in x245a.find(source))
    try:
        return vals.next()
    except StopIteration:
        return 'NA'

@app.route("/authors/<index>/<id>")
def authors(index, id):
    es = elasticsearch.Elasticsearch()
    source = es.get_source(index=index, id=id)
    value = xauthors(source).strip()
    if not value:
        value = "NA"
    return value


@app.route("/pages/<index>/<id>")
def pages(index, id):
    es = elasticsearch.Elasticsearch()
    source = es.get_source(index=index, id=id)
    vals = (match.value for match in x300a.find(source))
    try:
        return vals.next()
    except StopIteration:
        return 'NA'


@app.route("/")
def hello():
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
