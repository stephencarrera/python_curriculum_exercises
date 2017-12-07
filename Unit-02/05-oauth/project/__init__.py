from flask import Flask, redirect, url_for, render_template
from flask_modus import Modus
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_oauthlib.client import OAuth

import os



app = Flask(__name__)
app.url_map.strict_slashes = False
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
oauth = OAuth(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://localhost/users-messages-bcrypt'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["CONSUMER_KEY"] = os.environ.get('CONSUMER_KEY')
app.config["CONSUMER_SECRET"] = os.environ.get('CONSUMER_SECRET')

modus = Modus(app)
moment = Moment(app)
db = SQLAlchemy(app)

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=os.environ.get('CONSUMER_KEY'),
    consumer_secret=os.environ.get('CONSUMER_SECRET')
)


from project.users.views import users_blueprint
from project.messages.views import messages_blueprint
from project.tags.views import tags_blueprint

app.register_blueprint(users_blueprint, url_prefix='/users')
app.register_blueprint(messages_blueprint, url_prefix='/users/<int:user_id>/messages')
app.register_blueprint(tags_blueprint, url_prefix='/tags')

login_manager.login_view = "users.login"

from project.models import User



@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/')
def root():
	return redirect(url_for('users.index'))

@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/auth/twitter/callback')
def oauth_authorized():
    next_url = request.args.get('next') or url_for('users.index')
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
        return redirect(next_url)

    # add some information to the session
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    return redirect(next_url)

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


@app.errorhandler(404)
def page_not_found(error):
	return render_template('errors.html', error=error), 404

@app.errorhandler(500)
def server_error(error):
	return render_template('errors.html', error=error), 500