from __future__ import absolute_import
from flask import Blueprint, jsonify, Flask, url_for, render_template, request, current_app
from jinja2 import Environment, FileSystemLoader
from Application import TweetSearch

App = Blueprint('main', __name__, url_prefix="/test")

env = Environment(loader = FileSystemLoader('templates'))

@App.route('/',methods=['GET', 'POST'])
def newproject(): 
  env = Environment(loader = FileSystemLoader('Application/templates'))
  home_temp = env.get_template('home.html')
  css_home = url_for('static', filename='home.css')
  if request.method == 'GET':
    return home_temp.render(css_home = css_home)
  if request.form['start'] == '>>':
    print('here')
    #TweetSearch.SearchTweets()
    TweetSearch.SearchTweets.delay()
    return home_temp.render(css_home = css_home)
    