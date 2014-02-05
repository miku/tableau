#!/usr/bin/env python

from config import SIMDB
from flask import Flask, render_template, redirect, request, url_for, jsonify, Response, send_from_directory
from utils import dbopen
import elasticsearch
import json
import os
import random

app = Flask(__name__)

@app.route('/static/images/bg.jpg')
def random_background():
    filename = random.choice(os.listdir('static/images'))
    print(filename)
    return send_from_directory('static/images', filename)

@app.route("/unrated")
def unrated():
    with dbopen(SIMDB) as cursor:
        cursor.execute("SELECT * from similarity limit 10")
        results = cursor.fetchall()
        print(results[0])
    return render_template('unrated.html', name='unrated', results=results)

@app.route("/pairs")
def pairs():
    with dbopen(SIMDB) as cursor:
        cursor.execute("SELECT distinct i1, i2, count(*) from similarity group by i1, i2")
        results = cursor.fetchall()
    return Response(json.dumps(results), mimetype="application/json")

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

@app.route("/compare")
def compare():
    with dbopen(SIMDB) as cursor:
        cursor.execute("SELECT * from similarity order by RANDOM() limit 1")
        result = cursor.fetchone()
    return render_template('compare.html', name='compare', result=result)

@app.route("/")
def hello():
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
