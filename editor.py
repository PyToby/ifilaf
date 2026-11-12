
from website import create_app
from website.models import Items
from website.extensions import db

from datetime import datetime


app = create_app()


def show_items():
    items = Items.query.order_by(Items.id).all()

    print("\n--- ITEMS ---")

    for item in items:
        print(
            f"ID: {item.id} | "
            f"Name: {item.name} | "
            f"Type: {item.type} | "
            f"User: {item.user_email}"
        )

    print(f"\nTotal: {len(items)}")


def show_item(item):
    print("\n--- ITEM DETAILS ---")

    for column in Items.__table__.columns:
        print(f"{column.name}: {getattr(item, column.name)}")


def edit_item(item):
    print("\nEnter new values (leave empty to keep current value).")

    for column in Items.__table__.columns:
        name = column.name

        if name == "id":
            continue

        old_value = getattr(item, name)
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
            else:
                value = new_value

            setattr(item, name, value)

        except (ValueError, TypeError):
            print("Invalid value! Keeping old value.")

    db.session.commit()
    print("Item updated!")


def add_item():
    print("\n--- ADD ITEM ---")

    item = Items()

    for column in Items.__table__.columns:
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

            setattr(item, name, value)

        except (ValueError, TypeError):
            print("Invalid value!")
            return

    db.session.add(item)
    db.session.commit()

    print(f"Item added! ID: {item.id}")


def delete_item(item):
    confirm = input(f"Delete item {item.id} permanently? (y/n): ")

    if confirm.lower() == "y":
        db.session.delete(item)
        db.session.commit()
        print("Item deleted!")


def main():
    with app.app_context():

        while True:
            print("""
========== DATABASE EDITOR ==========

1. Show all items
2. Show item details
3. Edit item
4. Add item
5. Delete item
0. Exit

=====================================
""")

            choice = input("Choice: ")

            try:
                if choice == "1":
                    show_items()

                elif choice in ("2", "3", "5"):
                    item_id = int(input("Item ID: "))
                    item = db.session.get(Items, item_id)

                    if item is None:
                        print("Item not found!")
                        continue

                    if choice == "2":
                        show_item(item)

                    elif choice == "3":
                        edit_item(item)

                    elif choice == "5":
                        delete_item(item)

                elif choice == "4":
                    add_item()

                elif choice == "0":
                    break

                else:
                    print("Unknown option!")

            except Exception as e:
                db.session.rollback()
                print(f"Database error: {e}")


if __name__ == "__main__":
    main()
