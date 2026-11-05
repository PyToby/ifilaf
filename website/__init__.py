from flask import Flask, session
from .extensions import db, login_manager
import os, sys, logging, dotenv

dotenv.load_dotenv()  

# --- Logging Setup ---
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# --- Flask App Setup ---
DB_NAME = 'database.db'

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,  # drops stale connections automatically
        "pool_size": 5,
        "max_overflow": 10,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    from .models import Items

    login_manager.init_app(app)

    from .views import view
    from .auth import auth

    app.register_blueprint(view, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')

    create_database(app)

    return app

def create_database(app):
    db_path = os.path.join(app.instance_path, DB_NAME)

    with app.app_context():
        db.create_all()
        print('Created database!')

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))