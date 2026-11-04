# Lost & Found

A web application for managing lost and found items at **Gymnázium Jana Keplera (gjk.cz)**. Students and staff can report found items and browse what has been handed in. 

## Features

- **Restricted authentication**: Only `@gjk.cz` email addresses can register and log in
- **Lost & found items**: Create, view, edit, and delete item records
- **Ownership control**: Users manage the items they posted

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Authentication | Flask-Login, Google Authentication |
| Database / ORM | SQLAlchemy (SQLite by default) |
| Templates | Jinja2, HTML, CSS |

## Project Structure

```
ifilaf/
├── website/
│   ├── __init__.py        # App initiation
│   ├── models.py          # Database table models
│   ├── views.py           # Routes
│   ├── extensions.py      # LoginManager and Database loader
│   ├── templates/         # Jinja2 templates
│   │   └── components/    # Individual item-card and similar frontend components
│   └── static/            # CSS, JS, images
│       ├── css/
│       └── js/
├── requirements.txt
├── main.py                # Entry point
├── .gitignore
└── README.md
```

## Getting Started

In the near future, a temporary website will be spun up for **development and testing purposes only**.


## Usage

1. Register or log in with your `@gjk.cz` email.
2. Browse found items on the home page (paginated).
3. Click **Add item** to report something you found.
4. Edit or delete your own entries when an item has been returned.

## Authors

Special thanks to [@jeohan19](https://www.github.com/jeohan19) and [@Onkvisu](https://www.github.com/onkvisu) for being able to develop this project. _Can be found in contributors tab._