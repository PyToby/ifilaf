from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from supabase import create_client

db = SQLAlchemy()
login_manager = LoginManager()

oauth = OAuth()

class SupabaseStorage:
    def init_app(self, app):
        self.client = create_client(
            app.config["SUPABASE_URL"],
            app.config["SUPABASE_KEY"],
        )
        self.bucket = self.client.storage.from_(app.config["SUPABASE_BUCKET"])

storage = SupabaseStorage()