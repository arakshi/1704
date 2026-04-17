from __future__ import annotations

from flask import Flask

from app.config import Config
from app.models import db
from app.routes.accountant import accountant_bp
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.core import core_bp
from app.routes.driver import driver_bp
from app.services.bootstrap import ensure_directories, seed_demo_documents, seed_demo_users


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    ensure_directories(app)
    db.init_app(app)

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(accountant_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        seed_demo_users()
        seed_demo_documents(app.config["UPLOAD_FOLDER"], force=False)

    return app
