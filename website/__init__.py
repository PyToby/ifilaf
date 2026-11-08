from flask import Flask
from .extensions import db, login_manager, oauth
import os
import sys
import logging
import dotenv
from .models import Items

dotenv.load_dotenv()  

# --- Logging Setup ---
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# --- Flask App Setup ---
DB_NAME = 'database.db'


def create_app():
    app = Flask(__name__)

    # --- Security ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    if not app.config['SECRET_KEY']:
        raise RuntimeError("SECRET_KEY is not configured")

    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    # --- Database ---
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    if database_url.startswith('postgres://'):
        database_url = database_url.replace(
            'postgres://', 'postgresql://', 1
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,  # drops stale connections automatically
        "pool_size": 5,
        "max_overflow": 10,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- Extensions ---
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # --- Google OAuth ---
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get(
        'GOOGLE_CLIENT_SECRET'
    )

    if not app.config['GOOGLE_CLIENT_ID']:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")

    if not app.config['GOOGLE_CLIENT_SECRET']:
        raise RuntimeError("GOOGLE_CLIENT_SECRET is not configured")

    oauth.init_app(app)

    oauth.register(
        name='google',
        server_metadata_url=(
            'https://accounts.google.com/.well-known/openid-configuration'
        ),
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # --- Blueprints ---
    from .models import Items

    from .views import view
    from .auth import auth

    app.register_blueprint(view, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')

    # --- Database Creation ---
    create_database(app)

    return app


def create_database(app):
    with app.app_context():
        db.create_all()
        print('Created database!')

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.session.get(User, int(user_id))
