from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from .models import Items, Image
from .extensions import db

view = Blueprint('view', __name__)

class Item_Data:
    def __init__(self, item):
        self.name = item.name
        self.description = item.description
        self.type = item.type
        self.state = item.state
        self.category = item.category
        self.table = {
            "date": item.date,
            "location": item.location,
            "prize": item.prize
        }
        self.__item__ = item
    def authenticated(self): #add details for authenticated users
        self.table["email"] = self.__item__.user_email
        

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
        type = request.form.get('type')
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        #images = request.form.get('photo')
        location = request.form.get('location')
        date = request.form.get('date')
        prize = request.form.get('prize')

        if type == 'lost':
            current_location = request.form.get('current_location')

            new_item = Items(
                name=name,
                description=description,
                type='lost',
                prize=prize,
                date=date,
                location=location,
                current_location=current_location,
                category=category,
                user_email=current_user.email,   # required, see below
            )

            db.session.add(new_item)
            db.session.commit()
        new_item = Items(
            name=name,
            description=description,
            type='found',
            prize=prize,
            date=date,
            location=location,
            current_location=current_location,
            category=category,
            user_email=current_user.email,   # required, see below
        )

        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("view.home"))
    return render_template('item_add.html', categories=['Electronics', 'Clothing', 'Other'])
