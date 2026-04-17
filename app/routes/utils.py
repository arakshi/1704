from __future__ import annotations

from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Войдите в систему.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("role") not in roles:
                flash("Недостаточно прав для доступа к разделу.", "danger")
                return redirect(url_for("core.index"))
            return view(*args, **kwargs)

        return wrapped

    return decorator
