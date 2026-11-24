from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required
from .models import Items, Image, User
from .extensions import db, storage
import uuid

view = Blueprint('view', __name__)

CATEGORIES = ['Electronics', 'Clothing', 'Other']
FILTERS=['All', 'Lost', 'Found', 'Archived']



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

def find_users_query(searched_string):
    """
    Find users by email or name.
    """
    query = User.query
    if searched_string:
        query = query.filter(User.email.ilike(f"%{searched_string}%") | User.name.ilike(f"%{searched_string}%"))
    return query

@view.route('/')
def home():
    """
    The function returning the homepage for everyone and deciding whether to display a logged in version or not.
    """
    filter_type = request.args.get('filter')
    if filter_type is None or filter_type == 'all':
        items = Items.query.all()
    elif filter_type in ['lost', 'found']:
        items = Items.query.filter_by(type=filter_type).all()
    elif filter_type == 'archived':
        items = Items.query.filter_by(state='archived').all()
    elif filter_type == 'mine':
        items = Items.query.filter_by(user_email=current_user.email).all()


    if current_user.is_authenticated:
        print(f'Current user: {current_user.is_authenticated}')
        return render_template('home.html', current_user=current_user, name=current_user.name, items=items, filters=['All', 'Mine', 'Lost', 'Found', 'Archived'])
    return render_template('home.html', current_user=False, items=items, filters=FILTERS)

ALLOWED_EXTENSIONS = ['png', 'jpg', 'webp', 'jpeg']
def allowed_extensions(file: str) -> bool: 
    """
    A function to determine if a file extension is allowed.

    :param file: Takes the file name.
    :return: True or False
    """
    if file.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return True
    return False

def save_photos(files) -> list:
    """
    A function used by /add-item to save images to a db bucket.
    
    :param files: Takes the file objects requested from the html form.
    :return: A list of file names to then save to a db table seperately
    """
    saved = []
    for f in files:
        if not f or not f.filename:
            continue
        if not allowed_extensions(f.filename):
            continue

        # Picking a random name to avoid problems because I hate users...
        ext = f.filename.rsplit(".", 1)[1].lower()
        path = f"uploads/{uuid.uuid4().hex}.{ext}" # The whole path in the specific bucket

        storage.bucket.upload(path=path, file=f.read(), file_options={"content-type": f.mimetype})
        saved.append(path)
    return saved


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
        image_paths = save_photos(request.files.getlist("photo"))
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
        db.session.flush() # to add new_item in order to then retrieve its id given by the db 

        for i, image in enumerate(image_paths):
            db.session.add(Image(
                pos=i,
                image_path=image,
                item_id=new_item.id,
            ))

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

    saved = request.args.get('saved') == '1'

    return render_template(
        "item_detail.html",
        current_user=current_user,
        item=item,
        item_id=item.id,
        editing=editable and (request.method == 'POST' or request.args.get('edit') == '1'),
        can_edit=editable,
        categories=categories_for(item),
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
    return render_template('administration.html', current_user=current_user, admins=admins, search_query='')

@view.route("/administration/search_admins")
@login_required
def search_admins():
    """
    Route to search for administrators by email or name.
    """
    if not current_user.is_admin:
        abort(403)

    query = request.args.get("search_for_admins", "")

    users = find_users_query(query)
    admins = users.filter_by(is_admin=True).all()
    return render_template('administration.html', current_user=current_user, admins=admins, search_query=query)

@view.route("/administration/search_users")
@login_required
def search_users():
    """
    Route to search for users by email or name.
    """
    if not current_user.is_admin:
        abort(403)

    query = request.args.get("search_for_users", "")

    users = find_users_query(query).filter_by(is_admin=False).all()
    return render_template('add_admin.html', current_user=current_user, users=users, search_query=query)

@view.route("/administration/delete_admin/<int:user_id>")
@login_required
def delete_admin(user_id):
    """
    Route to delete an admin account from the database
    """
    if not current_user.is_admin:
        abort(403)

    user = User.query.get(user_id)
    if user is None or not user.is_admin:
        abort(404)

    user.is_admin = False
    db.session.commit()
    return redirect(url_for('view.display_administration'))

@view.route("/administration/add_admin/")
@login_required
def display_add_admin():
    if not current_user.is_admin:
        abort(403)
        
    users = User.query.filter_by(is_admin=False).all()
    return render_template('add_admin.html', current_user=current_user, users=users, search_query='')

@view.route("/administration/add_admin/<int:user_id>")
@login_required
def add_admin(user_id):
    """
    Route to add an admin account to the database
    """
    if not current_user.is_admin:
        abort(403)

    user = User.query.get(user_id)
    if user is None or user.is_admin:
        abort(404)

    user.is_admin = True
    db.session.commit()
    return redirect(url_for('view.display_add_admin'))