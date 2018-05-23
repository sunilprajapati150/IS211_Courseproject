#!/usr/bin/python
# -*- coding: utf-8 -*-
"""IS211. Final"""

import urllib2
from flask import Flask, render_template, request, redirect, session, g, url_for, abort, flash
import pickle
import os.path
import time
import re
import json
import sqlite3
import requests
from contextlib import closing

DATABASE = 'bookcatalogue.db'
DEBUG = True
SECRET_KEY = 'use os.urandom(24) to generate'
USERNAME = 'admin'
PASSWORD = 'password'

web_app = Flask(__name__)
web_app.config.from_object(__name__)

API_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

def connect_db():
    return sqlite3.connect(web_app.config['DATABASE'])


@web_app.before_request
def before_request():
    g.db = connect_db()


@web_app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@web_app.route('/google_api', methods=['POST', 'GET'])
def google_api():
    if request.method == 'POST':
        isbn = request.form['ISBN']
        if isbn == "":
            flash("Please Enter an ISBN Number")
            return redirect(url_for('google_api'))
        else:
            try:
                url = API_URL + isbn
                html = urllib2.urlopen(url)
                data = html.read()
                data = json.loads(data)
                volumeinfo = data['items'][0]['volumeInfo']
                title = volumeinfo['title']
                authors = volumeinfo['authors'][0]
                pagecount = volumeinfo['pageCount']
                averagerating = volumeinfo['averageRating']
                thumbnail = volumeinfo['imageLinks']['smallThumbnail']
                return render_template('google_api.html', thumbnail=thumbnail,
                                       title=title, authors=authors,
                                       pagecount=pagecount,
                                       averagerating=averagerating, isbn=isbn)
            except google_apiError:
                flash("ISBN google_api error")
                return redirect(url_for('google_api'))
    if request.method == 'GET':
        return render_template('google_api.html')


@web_app.route('/add', methods=['POST'])
def add():
    if not session.get('logged_in'):
        abort(401)
    try:
        g.db.execute('INSERT INTO bookcatalogue (ISBN, TITLE, AUTHORS, PAGECOUNT, '
                     'AVERAGERATING, THUMBNAIL) values (?, ?, ?, ?, ?, ?)',
                     (request.form['isbn'], request.form['title'],
                      request.form['authors'], request.form['pagecount'],
                      request.form['averagerating'], request.form['thumbnail']))
        g.db.commit()
        flash("Book added to your list")
        return redirect(url_for('homepage'))
    except():
        flash("unable to add,please try again")
        return redirect(url_for('homepage'))


@web_app.route('/delete', methods=['GET'])
def delete():
    book_id = request.args.get('id')
    g.db.execute('DELETE FROM bookcatalogue WHERE ID = ?', book_id)
    g.db.commit()
    flash("Deleted library item")
    return redirect(url_for('homepage'))


@web_app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if 
		session['logged_in'] = True
            flash("Welcome!! Your current library is displayed below.")
            return redirect(url_for('homepage'))
		
		
		elif request.form['username'] != web_app.config['USERNAME']:
            error = "Invalid Username"
            flash("Username not found")
			
         else request.form['password'] != web_app.config['PASSWORD']:
            error = "Invalid Password"
            flash("Sorry.wrong password")
        
            
    return render_template('login.html', error=error)


@web_app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You were logged out")
    return redirect(url_for('homepage'))


@web_app.route('/')
def homepage():
    cur = g.db.execute('SELECT ID, ISBN, TITLE, AUTHORS, PAGECOUNT, '
                       'AVERAGERATING, THUMBNAIL FROM bookcatalogue')
    bookcatalogue = [dict(id=row[0], isbn=row[1], title=row[2], authors=row[3],
                  pagecount=row[4], averagerating=row[5],
                  thumbnail=row[6]) for row in cur.fetchall()]
    return render_template('login.html', bookcatalogue=bookcatalogue)


if __name__ == "__main__":
    web_app.run()
