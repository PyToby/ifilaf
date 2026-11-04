from flask import Blueprint, render_template, request, jsonify, Response, session, current_app
from flask_login import current_user, login_required
from .models import Items
from .extensions import db

view = Blueprint('view', __name__)

@view.route('/')
def home():
    """
    The function returning the homepage for everyone and deciding whether to display a logged in version or not.
    """

    items = Items.query.all()

    if current_user.is_authenticated:
        print(f'Current user: {current_user.is_authenticated}')
        return render_template('home.html', current_user, name=current_user.name)
    return render_template('home.html', current_user=False, items=items)

