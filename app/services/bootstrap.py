from __future__ import annotations

from pathlib import Path

from app.models import User, UserRole, db


def ensure_directories(app) -> None:
    for folder in [app.config["UPLOAD_FOLDER"], app.config["EXPORT_FOLDER"], app.config["INSTANCE_FOLDER"]]:
        Path(folder).mkdir(parents=True, exist_ok=True)

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        sqlite_file = Path(db_uri.replace("sqlite:///", "", 1))
        sqlite_file.parent.mkdir(parents=True, exist_ok=True)


def seed_demo_users() -> None:
    if User.query.count() > 0:
        return

    demo_users = [
        ("driver", "123456", UserRole.DRIVER.value, "Демо Водитель"),
        ("accountant", "123456", UserRole.ACCOUNTANT.value, "Демо Бухгалтер"),
        ("admin", "123456", UserRole.ADMIN.value, "Демо Админ"),
    ]

    for username, password, role, full_name in demo_users:
        user = User(username=username, role=role, full_name=full_name)
        user.set_password(password)
        db.session.add(user)

    db.session.commit()


def reset_database() -> None:
    db.drop_all()
    db.create_all()
    seed_demo_users()
