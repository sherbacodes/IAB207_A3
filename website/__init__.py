from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import datetime
import os

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    Bootstrap5(app)

    app.secret_key = os.getenv('SECRET_KEY', 'devkey')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'img')

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from . import views
    app.register_blueprint(views.main_bp)

    try:
        from . import events as events_module
        app.register_blueprint(events_module.eventbp)
    except ImportError:
        print("Warning: events.py not found. Skipping its registration.")

    from . import auth
    app.register_blueprint(auth.auth_bp)

    # 404 error handler
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html", error=e)
    
    # 500 error handler
    @app.errorhandler(500)
    def not_found(e):
        return render_template("500.html", error=e)

    # Inject current year into templates
    @app.context_processor
    def get_context():
        return dict(year=datetime.datetime.today().year)

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app