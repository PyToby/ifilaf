from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from .extensions import oauth, db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    google = oauth.create_client('google')

    redirect_uri = url_for(
        'auth.callback',
        _external=True
    )

    return google.authorize_redirect(redirect_uri)


@auth.route('/login/callback')
def callback():
    google = oauth.create_client('google')

    try:
        # Exchange authorization code for tokens.
        token = google.authorize_access_token()

        # Authlib verifies the ID token and extracts user information.
        userinfo = token.get('userinfo')

        if not userinfo:
            flash('Google did not return user information.', 'error')
            return redirect(url_for('view.home'))

        email = userinfo.get('email')
        email_verified = userinfo.get('email_verified')

        if not email or email_verified is not True:
            flash('Google email is not verified.', 'error')
            return redirect(url_for('view.home'))

        # Optional: restrict access to a specific email domain.
        # Replace with the actual domain if this restriction is needed.
        # if not email.lower().endswith('@example.com'):
        #     flash('Your email domain is not allowed.', 'error')
        #     return redirect(url_for('view.home'))

        google_sub = userinfo.get('sub')

        if not google_sub:
            flash('Google user ID is missing.', 'error')
            return redirect(url_for('view.home'))

        # First, search by Google's stable user identifier.
        user = User.query.filter_by(google_sub=google_sub).first()

        if user is None:
            # Check whether an account with this email already exists.
            user = User.query.filter_by(email=email.lower()).first()

            if user is not None:
                # Link the existing account to Google.
                if user.google_sub and user.google_sub != google_sub:
                    flash('This email is linked to another Google account.', 'error')
                    return redirect(url_for('view.home'))

                user.google_sub = google_sub

            else:
                # Create a new account.
                user = User(
                    email=email.lower(),
                    name=userinfo.get('name') or email,
                    pfp=userinfo.get('picture'),
                    google_sub=google_sub
                )

                db.session.add(user)

        # Save changes.
        db.session.commit()

        # Start Flask-Login session.
        login_user(user)

        return redirect(url_for('view.home'))

    except Exception:
        db.session.rollback()
        current_app.logger.exception('Google authentication failed')
        flash('Google authentication failed.', 'error')
        return redirect(url_for('view.home'))


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('view.home'))
