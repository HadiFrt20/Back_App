from flask import Blueprint, url_for, request, redirect, session
from jinja2 import Environment, FileSystemLoader
from CollectService import tasks

App = Blueprint('main', __name__, url_prefix="/admin")

env = Environment(loader=FileSystemLoader('templates'))


@App.route('/')
def index():
    return redirect(url_for('main.login'))


@App.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    env = Environment(loader=FileSystemLoader('Application/templates'))
    css_init = url_for('static', filename='init.css')
    if request.method == 'POST':
        print(request.form['username'])
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = request.form['username']
            session['logged'] = "in"
            return redirect(url_for('main.dashboard'))
    login_temp = env.get_template('login.html')
    return login_temp.render(css_init=css_init, error=error)


@App.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    env = Environment(loader=FileSystemLoader('Application/templates'))
    home_temp = env.get_template('home.html')
    css_home = url_for('static', filename='init.css')
    if session.get('logged') == "in":
        user = session.get('username')
        if request.method == 'GET':
            return home_temp.render(css_home=css_home, user=user)
        if request.method == 'POST':
            if request.form.get('logout') == 'Log Out':
                session.clear()
                return redirect(url_for('main.login'))
            elif request.form['start'] == 'Start':
                tasks.gettweets()
                return home_temp.render(css_home=css_home, user=user)

    else:
        error = "Permission denied : admin is not logged in"
        return redirect(url_for('main.login', error=error))
