from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash("Неверный логин или пароль.", "danger")
            return render_template("auth/login.html")

        session["user_id"] = user.id
        session["role"] = user.role
        session["full_name"] = user.full_name
        flash(f"Добро пожаловать, {user.full_name}!", "success")
        return redirect(url_for("core.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))
