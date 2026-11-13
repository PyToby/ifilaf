from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required

from .models import Items, Image, User
from .extensions import db

view = Blueprint('view', __name__)

CATEGORIES = ['Electronics', 'Clothing', 'Other']


class Item_Data:
    """
    Template-facing view of an item: the detail page and the inline edit form
    both read the same flat attributes from it.
    """

    def __init__(self, item):
        self.id = item.id
        self.name = item.name
        self.description = item.description
        self.type = item.type
        self.status = item.state
        self.category = item.category
        self.date = item.date
        self.location = item.location
        self.prize = item.prize
        self.current_location = item.current_location
        self.owner_email = item.user_email
        self.photo = item.images[0].image_path if item.images else None
        self.__item__ = item

    @property
    def color(self):
        """The form component calls the prize field 'color'."""
        return self.prize


def categories_for(item):
    """
    Category choices for the form, keeping a custom value selectable.
    """
    if item.category and item.category not in CATEGORIES:
        return CATEGORIES + [item.category]
    return CATEGORIES


def can_edit_item(item):
    """
    Only the owner or an admin may edit an item.
    """
    return current_user.is_authenticated and (
        current_user.is_admin or current_user.email == item.user_email
    )


def parse_date(value):
    """
    Parse a <input type="datetime-local"> value. Returns (datetime|None, error).
    """
    if not value:
        return None, False
    try:
        return datetime.fromisoformat(value), False
    except ValueError:
        return None, True


@view.route('/')
def home():
    """
    The function returning the homepage for everyone and deciding whether to display a logged in version or not.
    """

    items = Items.query.all()

    if current_user.is_authenticated:
        print(f'Current user: {current_user.is_authenticated}')
        return render_template('home.html', current_user=current_user, name=current_user.name, items=items)
    return render_template('home.html', current_user=False, items=items)


@view.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    """
    The route to add a new item to the database by an authenticated user, hence the @login_required decorator..
    """
    if request.method == 'POST':
        type = request.form.get('type')
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        #images = request.form.get('photo')
        location = request.form.get('location')
        date = request.form.get('date')
        prize = request.form.get('prize')

        if type == 'found':
            current_location = request.form.get('current_location')

            new_item = Items(
                name=name,
                description=description,
                type=type,
                prize=prize,
                date=date,
                location=location,
                current_location=current_location,
                category=category,
                user_email=current_user.email,
            )
        else:
            new_item = Items(
                name=name,
                description=description,
                type=type,
                prize=prize,
                date=date,
                location=location,
                category=category,
                user_email=current_user.email,
            )

        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("view.home"))
    return render_template('item_add.html', categories=CATEGORIES)


@view.route("/item/<int:item_id>", methods=['GET', 'POST'])
def display_item_detail(item_id):
    """
    Route to display a specific item detail page.

    Owners and admins can edit the item in place: the page renders the same
    item_detail.html, with editable fields instead of plain values. The form
    posts back to this same URL.

    :param item_id: the item id
    :return: the rendered detail page
    """
    item = Items.query.filter_by(id=item_id).first()

    if item is None:
        abort(404)

    editable = can_edit_item(item)
    values = None
    errors = None

    if request.method == 'POST':
        if not editable:
            abort(403)

        values = request.form.to_dict()
        errors = {}

        name = (values.get('name') or '').strip()
        location = (values.get('location') or '').strip()
        type = values.get('type') if values.get('type') in ('lost', 'found') else 'lost'
        date, date_invalid = parse_date(values.get('date'))

        if not name:
            errors['name'] = 'Give the item a name.'
        if not location:
            errors['location'] = 'Add where it was lost or found.'
        if date_invalid:
            errors['date'] = 'Enter a valid date and time.'

        if not errors:
            item.name = name
            item.type = type
            item.category = values.get('category') or None
            item.description = values.get('description') or ''
            item.location = location
            item.date = date
            item.prize = values.get('prize') or None
            item.current_location = (
                values.get('current_location') or None if type == 'found' else None
            )

            db.session.commit()
            return redirect(
                url_for('view.display_item_detail', item_id=item.id, saved=1)
            )

    item_data = Item_Data(item)

    saved = request.args.get('saved') == '1'

    return render_template(
        "item_detail.html",
        current_user=current_user,
        item=item_data,
        item_id=item.id,
        editing=editable and (request.method == 'POST' or request.args.get('edit') == '1'),
        can_edit=editable,
        categories=categories_for(item_data),
        values=values,
        errors=errors,
        submit_label='Save changes',
        show_contact=current_user.is_authenticated,
        flash_success='Changes saved.' if saved else None,
    )

@view.route("/administration")
@login_required
def display_administration():
    """
    Route to display the administration page for editing admin accounts
    """
    if not current_user.is_admin:
        abort(403)

    admins = User.query.filter_by(is_admin=True).all()
    return render_template('administration.html', current_user=current_user, admins=admins)