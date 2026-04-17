from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, url_for

from app.models import Document, User
from app.routes.utils import login_required, role_required
from app.services.bootstrap import reset_database, seed_default_users, seed_sample_documents

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    documents = Document.query.order_by(Document.uploaded_at.desc()).limit(100).all()
    return render_template("admin/dashboard.html", users=users, documents=documents)


@admin_bp.post("/create-samples")
@login_required
@role_required("admin")
def create_samples():
    base_users = seed_default_users()
    created_docs = seed_sample_documents(current_app.config["UPLOAD_FOLDER"], force=False)
    if created_docs:
        flash(f"Начальные данные созданы: пользователей {len(base_users)}, документов {created_docs}.", "success")
    else:
        flash("Пользователи уже есть, новых документов не добавлено (реестр уже заполнен).", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/reset-db")
@login_required
@role_required("admin")
def reset_db():
    reset_database()
    seed_sample_documents(current_app.config["UPLOAD_FOLDER"], force=True)
    flash("БД сброшена и заново инициализирована.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/reinit")
@login_required
@role_required("admin")
def reinit():
    reset_database()
    seed_sample_documents(current_app.config["UPLOAD_FOLDER"], force=True)
    flash("Проект переинициализирован.", "info")
    return redirect(url_for("admin.dashboard"))
