import os
from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, logout_user
from flask_dance.contrib.github import github
from flask_dance.contrib.google import google
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = 'tHiS-iS-a-H@rD-tO-gUeSs-sTrInG'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from oauth import github_blueprint, google_blueprint
app.register_blueprint(github_blueprint, url_prefix='/login')
app.register_blueprint(google_blueprint, url_prefix='/login')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    user_info = github.get('/user').json()
    email_info = github.get('/user/emails').json()
    
    user_data = {
        'username': user_info.get('login', 'N/A'),
        'email': email_info[0]['email'] if email_info else 'N/A',
        'public_repos': user_info.get('public_repos', 0),
        'created_at': user_info.get('created_at', 'N/A'),
        'avatar_url': user_info.get('avatar_url', 'N/A')
    }
    return render_template('index.html', user_data=user_data)

@app.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    user_info = google.get('/oauth2/v2/userinfo').json()
    
    user_data = {
        'username': user_info.get('name', 'N/A'),
        'email': user_info.get('email', 'N/A'),
        'public_repos': 'N/A',
        'created_at': 'N/A',
        'avatar_url': user_info.get('picture', 'N/A')
    }
    return render_template('index.html', user_data=user_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/test')
def test_func():
    return jsonify(test="200 OK")