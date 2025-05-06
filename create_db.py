# This script creates the database for the Flask application.
# It initializes the Flask application context and creates all the tables defined in the models.
from website import db, create_app
app = create_app()
ctx = app.app_context()
ctx.push()
db.create_all()
quit()