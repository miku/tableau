#!/usr/bin/env python

from flask import Flask, render_template, redirect, request, url_for
app = Flask(__name__)

SIMDB = ""

@app.route("/unrated")
def unrated():
    return render_template('index.html', name='unrated')

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

@app.route("/")
def hello():
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
