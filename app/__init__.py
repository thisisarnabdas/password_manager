from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from app.config import Config
from argon2 import PasswordHasher

ph = PasswordHasher()
db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # Import and register the blueprint
    from app.controller import controller
    app.register_blueprint(controller)
    return app


app = create_app()
