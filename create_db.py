# This script creates the database for the Flask application.
# It initializes the Flask application context and creates all the tables defined in the models.
from website import db, create_app
from website.models import Category

app = create_app()
ctx = app.app_context()
ctx.push()
db.create_all()

default_categories = [
    "Classical", "Pop", "Rock", "Hip-Hop", "Rap",
    "Country", "Jazz", "Electronic"
]

for name in default_categories:
    if not Category.query.filter_by(name=name).first():
        db.session.add(Category(name=name))

db.session.commit()
quit()