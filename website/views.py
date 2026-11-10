from flask import Blueprint, render_template, request, jsonify, Response, session, current_app
from flask_login import current_user, login_required
from .models import Items
from .extensions import db

view = Blueprint('view', __name__)

class Item_Data:
    def __init__(self, name=None, description=None, table=None, type=None, state=None, pictures=None):
        self.name = name
        self.pictures = pictures
        self.description = description
        self.table = table
        self.type = type
        self.state = state

@view.route('/')
def home():
    """
    The function returning the homepage for everyone and deciding whether to display a logged in version or not.
    """

    items = Items.query.all()

    if current_user.is_authenticated:
        print(f'Current user: {current_user.is_authenticated}')
        return render_template('home.html',current_user=current_user, name=current_user.name, items=items)
    return render_template('home.html', current_user=False, items=items)

@view.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        #logika pro ukladani
        pass

    return render_template('add_item.html')

@view.route("/item/<int:item_id>")
def display_item_detail(item_id):

    item = Items.query.filter_by(id=item_id).first()

    table = {
                "date":item.date,
                "location":item.location}

    item_data = Item_Data(item.name, item.description, table, item.type, item.state, item.pictures)

    if not current_user.is_authenticated:
        return render_template("item_detail.html",current_user=current_user, item=item_data)

    item_data.table["email"] = item.user_email

    if current_user.is_admin or current_user.email == item.email:
        return render_template("item_edit.html",current_user=current_user,user_id=current_user.id, name=current_user.name, pfp=current_user.pfp, is_admin=current_user.is_admin, item=item_data)

    else:
        return render_template("item_detail.html",current_user=current_user, user_id=current_user.id, name=current_user.name, pfp=current_user.pfp, item=item_data)