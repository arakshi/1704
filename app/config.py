from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _normalize_database_url(raw_url: str) -> str:
    raw_url = (raw_url or "").strip()

    if not raw_url:
        return f"sqlite:///{(BASE_DIR / 'instance' / 'app.db').as_posix()}"

    if raw_url.startswith("sqlite:///") and not raw_url.startswith("sqlite:////"):
        sqlite_path = raw_url.replace("sqlite:///", "", 1)
        candidate = Path(sqlite_path)
        if not candidate.is_absolute():
            candidate = BASE_DIR / candidate
        return f"sqlite:///{candidate.as_posix()}"

    return raw_url


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///instance/app.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    UPLOAD_FOLDER = str(BASE_DIR / os.getenv("UPLOAD_FOLDER", "uploads"))
    EXPORT_FOLDER = str(BASE_DIR / os.getenv("EXPORT_FOLDER", "exports"))
    INSTANCE_FOLDER = str(BASE_DIR / "instance")

    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
