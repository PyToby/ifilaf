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

@view.route('/')
def home():
    items = Items.query.all()

    if current_user.is_authenticated:
        name = current_user.name
    else:
        name = None

    return render_template(
        'home.html',
        current_user=current_user.is_authenticated,
        name=name,
        items=items
    )

@view.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        #logika pro ukladani
        pass

    return render_template('add_item.html')