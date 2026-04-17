from __future__ import annotations

from flask import Blueprint, redirect, render_template, session, url_for

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def index():
    role = session.get("role")
    if role == "driver":
        return redirect(url_for("driver.dashboard"))
    if role == "accountant":
        return redirect(url_for("accountant.registry"))
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    return render_template("index.html")
