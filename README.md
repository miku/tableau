README
======

Displaying data and gathering feedback.

Build and run
-------------

* Install dependencies

        $ mkvirtualenv tableau
        (tableau)$ pip install -r requirements.txt


* Development

        (tableau)$ python tableau/app.py


* More serious

        (tableau)$ gunicorn tableau.app:app
