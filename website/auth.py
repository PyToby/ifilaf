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
        token = google.authorize_access_token()
        userinfo = token.get('userinfo')

        if not userinfo:
            flash('Google did not return user information.', 'error')
            return redirect(url_for('view.home'))

        email = userinfo.get('email')
        email_verified = userinfo.get('email_verified')

        if not email or email_verified is not True:
            flash('Google email is not verified.', 'error')
            return redirect(url_for('view.home'))

        email = email.lower()
   
        if not email.endswith('@gjk.cz'):
            flash('Přihlášení je povoleno pouze pomocí školního e-mailu @gjk.cz.', 'error')
            return redirect(url_for('view.home'))


        user = User.query.filter_by(email=email).first()
        name = (userinfo.get('name') or '').strip()
        parts = name.split(maxsplit=1)

        firstname = parts[0] if parts else None
        surname = parts[1] if len(parts) > 1 else None


        user = User.query.filter_by(email=email).first()

        if user is None:
            user = User(
                email=email,
                name=name or email,
                firstname=firstname,
                surname=surname,
                pfp=userinfo.get('picture')
            )

            db.session.add(user)

        else:
            user.name = name or user.name
            user.firstname = firstname or user.firstname
            user.surname = surname or user.surname
            user.pfp = userinfo.get('picture') or user.pfp

        db.session.commit()

        login_user(user)

        return redirect(url_for('view.home'))

    except Exception:
        db.session.rollback()
        current_app.logger.exception('Google authentication failed')
        flash('Google authentication failed.', 'error')
        return redirect(url_for('view.home'))

@auth.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('view.home'))
