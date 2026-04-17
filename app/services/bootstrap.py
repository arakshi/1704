from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw

from app.models import Document, DocumentStatus, User, UserRole, db


def ensure_directories(app) -> None:
    for folder in [app.config["UPLOAD_FOLDER"], app.config["EXPORT_FOLDER"], app.config["INSTANCE_FOLDER"]]:
        Path(folder).mkdir(parents=True, exist_ok=True)

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        sqlite_file = Path(db_uri.replace("sqlite:///", "", 1))
        sqlite_file.parent.mkdir(parents=True, exist_ok=True)


def seed_demo_users() -> list[User]:
    existing = {u.username: u for u in User.query.all()}
    demo_users_data = [
        ("driver", "123456", UserRole.DRIVER.value, "Демо Водитель"),
        ("accountant", "123456", UserRole.ACCOUNTANT.value, "Демо Бухгалтер"),
        ("admin", "123456", UserRole.ADMIN.value, "Демо Админ"),
    ]

    changed = False
    for username, password, role, full_name in demo_users_data:
        if username in existing:
            continue
        user = User(username=username, role=role, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        changed = True

    if changed:
        db.session.commit()

    return User.query.filter(User.username.in_(["driver", "accountant", "admin"]))\
        .order_by(User.id.asc()).all()


def seed_demo_documents(upload_folder: str, force: bool = False) -> int:
    drivers = User.query.filter_by(role=UserRole.DRIVER.value).all()
    if not drivers:
        return 0

    if Document.query.count() > 0 and not force:
        return 0

    Path(upload_folder).mkdir(parents=True, exist_ok=True)

    statuses = [
        DocumentStatus.UNDER_REVIEW.value,
        DocumentStatus.ACCEPTED.value,
        DocumentStatus.REJECTED.value,
        DocumentStatus.NEED_REUPLOAD.value,
        DocumentStatus.AUTO_REJECTED.value,
    ]
    doc_types = ["ТТН", "Акт", "Счет-фактура"]
    counterparties = ["ООО Ромашка", "ООО Вектор", "АО Магистраль", "ИП Петров"]

    created = 0
    now = datetime.utcnow()

    for i in range(1, 11):
        driver = random.choice(drivers)
        status = statuses[(i - 1) % len(statuses)]
        file_name = f"demo_doc_{i:02d}.jpg"
        file_path = Path(upload_folder) / file_name
        _create_demo_image(file_path, f"DEMO #{i:02d}")

        uploaded_at = now - timedelta(days=i)
        doc = Document(
            order_number=f"ORD-{1000 + i}",
            document_type=random.choice(doc_types),
            file_name=file_name,
            original_name=file_name,
            status=status,
            status_comment="Нечеткое фото" if status in {DocumentStatus.REJECTED.value, DocumentStatus.NEED_REUPLOAD.value, DocumentStatus.AUTO_REJECTED.value} else None,
            ocr_available=True,
            ocr_text=f"DEMO OCR TEXT #{i}",
            doc_number=f"DOC-{2000 + i}",
            doc_date=date.today() - timedelta(days=i),
            amount=round(random.uniform(1500, 90000), 2),
            counterparty=random.choice(counterparties),
            quality_score=round(random.uniform(50, 100), 2),
            blur_metric=round(random.uniform(40, 180), 2),
            brightness_metric=round(random.uniform(30, 150), 2),
            width=1600,
            height=1200,
            uploaded_at=uploaded_at,
            reviewed_at=uploaded_at + timedelta(hours=2) if status in {DocumentStatus.ACCEPTED.value, DocumentStatus.REJECTED.value} else None,
            user_id=driver.id,
        )
        db.session.add(doc)
        created += 1

    db.session.commit()
    return created


def _create_demo_image(path: Path, caption: str) -> None:
    image = Image.new("RGB", (1600, 1200), color=(248, 250, 252))
    draw = ImageDraw.Draw(image)
    draw.rectangle((80, 80, 1520, 1120), outline=(90, 110, 140), width=4)
    draw.text((120, 120), "ООО Лик Транс", fill=(20, 30, 50))
    draw.text((120, 190), "Товарно-транспортная накладная", fill=(20, 30, 50))
    draw.text((120, 280), caption, fill=(0, 90, 180))
    draw.text((120, 360), "Этот файл создан автоматически как demo-данные.", fill=(40, 50, 70))
    image.save(path, format="JPEG", quality=92)


def reset_database() -> None:
    db.drop_all()
    db.create_all()
    seed_demo_users()
