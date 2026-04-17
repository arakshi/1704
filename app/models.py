from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class UserRole(str, Enum):
    DRIVER = "driver"
    ACCOUNTANT = "accountant"
    ADMIN = "admin"


class DocumentStatus(str, Enum):
    UNDER_REVIEW = "На проверке"
    ACCEPTED = "Принято"
    REJECTED = "Отклонено"
    NEED_REUPLOAD = "Требует повторной загрузки"
    AUTO_REJECTED = "Отклонено автоматически"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    documents = db.relationship("Document", backref="driver", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), nullable=False, index=True)
    document_type = db.Column(db.String(64), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)

    status = db.Column(db.String(50), default=DocumentStatus.UNDER_REVIEW.value, nullable=False, index=True)
    status_comment = db.Column(db.Text, nullable=True)

    ocr_available = db.Column(db.Boolean, default=True, nullable=False)
    ocr_text = db.Column(db.Text, nullable=True)
    doc_number = db.Column(db.String(128), nullable=True, index=True)
    doc_date = db.Column(db.Date, nullable=True, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=True, index=True)
    counterparty = db.Column(db.String(255), nullable=True, index=True)

    quality_score = db.Column(db.Float, nullable=True)
    blur_metric = db.Column(db.Float, nullable=True)
    brightness_metric = db.Column(db.Float, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    def amount_display(self) -> str:
        if self.amount is None:
            return ""
        return f"{self.amount:,.2f}".replace(",", " ")

    def set_amount(self, value: str | None) -> None:
        if not value:
            self.amount = None
            return
        normalized = value.replace(" ", "").replace(",", ".")
        try:
            self.amount = Decimal(normalized)
        except InvalidOperation:
            self.amount = None
