from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for

from app.models import Document, User
from app.routes.utils import login_required, role_required
from app.services.bootstrap import reset_database, seed_demo_users

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    documents = Document.query.order_by(Document.uploaded_at.desc()).limit(100).all()
    return render_template("admin/dashboard.html", users=users, documents=documents)


@admin_bp.post("/create-demo")
@login_required
@role_required("admin")
def create_demo():
    seed_demo_users()
    flash("Demo-пользователи созданы (если отсутствовали).", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/reset-db")
@login_required
@role_required("admin")
def reset_db():
    reset_database()
    flash("БД сброшена и заново инициализирована.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/reinit")
@login_required
@role_required("admin")
def reinit():
    reset_database()
    flash("Проект переинициализирован.", "info")
    return redirect(url_for("admin.dashboard"))
