
from website import create_app
from website.models import Items, User
from website.extensions import db

from datetime import datetime


app = create_app()


def edit_record(record):
    model = type(record)

    print("\nEnter new values (leave empty to keep current value).")

    for column in model.__table__.columns:
        name = column.name

        if name == "id":
            continue

        old_value = getattr(record, name)
        new_value = input(f"{name} [{old_value}]: ").strip()

        if new_value == "":
            continue

        try:
            python_type = column.type.python_type

            if python_type == datetime:
                value = datetime.fromisoformat(new_value)
            elif python_type == int:
                value = int(new_value)
            elif python_type == float:
                value = float(new_value)
            elif python_type == bool:
                value = new_value.lower() in ("true", "1", "yes")
            else:
                value = new_value

            setattr(record, name, value)

        except (ValueError, TypeError):
            print("Invalid value! Keeping old value.")

    try:
        db.session.commit()
        print("Record updated!")
    except Exception:
        db.session.rollback()
        raise


def add_record(model):
    print(f"\n--- ADD {model.__name__.upper()} ---")

    record = model()

    for column in model.__table__.columns:
        name = column.name

        if name == "id":
            continue

        value = input(f"{name}: ").strip()

        if value == "":
            continue

        try:
            python_type = column.type.python_type

            if python_type == datetime:
                value = datetime.fromisoformat(value)
            elif python_type == int:
                value = int(value)
            elif python_type == float:
                value = float(value)
            elif python_type == bool:
                value = value.lower() in ("true", "1", "yes")

            setattr(record, name, value)

        except (ValueError, TypeError):
            print("Invalid value!")
            return

    try:
        db.session.add(record)
        db.session.commit()
        print(f"Record added! ID: {record.id}")
    except Exception:
        db.session.rollback()
        raise


def delete_record(record):
    identifier = getattr(record, "email", None) or record.id

    confirm = input(
        f"Delete {type(record).__name__} {identifier} permanently? (y/n): "
    )

    if confirm.lower() == "y":
        db.session.delete(record)
        db.session.commit()
        print("Record deleted!")


def show_records(model):
    records = model.query.order_by(model.id).all()

    print(f"\n--- {model.__name__.upper()} ---")

    for record in records:
        if model == Items:
            print(
                f"ID: {record.id} | "
                f"Name: {record.name} | "
                f"Type: {record.type} | "
                f"User: {record.user_email}"
            )

        elif model == User:
            print(
                f"ID: {record.id} | "
                f"Email: {record.email} | "
                f"Name: {record.name} | "
                f"First name: {record.firstname} | "
                f"Surname: {record.surname}"
            )

    print(f"\nTotal: {len(records)}")


def show_record(record):
    print(f"\n--- {type(record).__name__.upper()} DETAILS ---")

    for column in type(record).__table__.columns:
        print(f"{column.name}: {getattr(record, column.name)}")


def manage_records(model, entity_name):
    while True:
        print(f"""
========== {entity_name.upper()} MANAGEMENT ==========

1. Show all {entity_name}
2. Show {entity_name} details
3. Edit {entity_name}
4. Add {entity_name}
5. Delete {entity_name}

0. Back

========================================
""")

        choice = input("Choice: ")

        try:
            if choice == "1":
                show_records(model)

            elif choice in ("2", "3", "5"):
                identifier = input(f"{entity_name.capitalize()} ID: ")

                try:
                    identifier = int(identifier)
                except ValueError:
                    print("Invalid ID!")
                    continue

                record = db.session.get(model, identifier)

                if record is None:
                    print(f"{entity_name.capitalize()} not found!")
                    continue

                if choice == "2":
                    show_record(record)

                elif choice == "3":
                    edit_record(record)

                elif choice == "5":
                    delete_record(record)

            elif choice == "4":
                add_record(model)

            elif choice == "0":
                break

            else:
                print("Unknown option!")

        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")


def main():
    with app.app_context():

        while True:
            print("""
========== DATABASE EDITOR ==========

1. Manage items
2. Manage users

0. Exit

=====================================
""")

            choice = input("Choice: ")

            if choice == "1":
                manage_records(Items, "items")

            elif choice == "2":
                manage_records(User, "users")

            elif choice == "0":
                break

            else:
                print("Unknown option!")


if __name__ == "__main__":
    main()
