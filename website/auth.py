from flask import Blueprint, redirect, request, url_for
from flask_login import login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import os

auth = Blueprint('auth', __name__)

# Currently to be set up, no ID or SECRET available
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@auth.route('/login')
def login():
    pass

@auth.route('/login/callback')
def callback():
    pass

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("view.home"))