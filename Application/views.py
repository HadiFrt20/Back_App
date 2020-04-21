from flask import Blueprint, url_for, request, current_app
from jinja2 import Environment, FileSystemLoader
from CollectService import tasks

App = Blueprint('main', __name__, url_prefix="/test")

env = Environment(loader=FileSystemLoader('templates'))


@App.route('/', methods=['GET', 'POST'])
def newproject():
    env = Environment(loader=FileSystemLoader('Application/templates'))
    home_temp = env.get_template('home.html')
    css_home = url_for('static', filename='home.css')
    if request.method == 'GET':
        return home_temp.render(css_home=css_home)
    if request.form['start'] == '>>':
        print(current_app._get_current_object())
        tasks.gettweets()
        return home_temp.render(css_home=css_home)
