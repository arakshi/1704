from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, send_from_directory, url_for

from app.models import Document, DocumentStatus, User, db
from app.routes.utils import login_required, role_required
from app.services.export_service import export_documents_to_excel

accountant_bp = Blueprint("accountant", __name__, url_prefix="/accountant")


def _base_query():
    return Document.query.join(User, Document.user_id == User.id)


def _apply_filters(query):
    status = request.args.get("status", "").strip()
    driver_id = request.args.get("driver_id", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    order_number = request.args.get("order_number", "").strip()
    doc_number_part = request.args.get("doc_number_part", "").strip()
    counterparty_part = request.args.get("counterparty_part", "").strip()
    amount_from = request.args.get("amount_from", "").strip()
    amount_to = request.args.get("amount_to", "").strip()

    if status:
        query = query.filter(Document.status == status)
    if driver_id.isdigit():
        query = query.filter(Document.user_id == int(driver_id))
    if date_from:
        try:
            query = query.filter(Document.uploaded_at >= datetime.strptime(date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Document.uploaded_at <= datetime.strptime(date_to, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    if order_number:
        query = query.filter(Document.order_number.ilike(f"%{order_number}%"))
    if doc_number_part:
        query = query.filter(Document.doc_number.ilike(f"%{doc_number_part}%"))
    if counterparty_part:
        query = query.filter(Document.counterparty.ilike(f"%{counterparty_part}%"))
    if amount_from:
        try:
            query = query.filter(Document.amount >= Decimal(amount_from.replace(",", ".")))
        except InvalidOperation:
            pass
    if amount_to:
        try:
            query = query.filter(Document.amount <= Decimal(amount_to.replace(",", ".")))
        except InvalidOperation:
            pass

    return query


@accountant_bp.route("/registry")
@login_required
@role_required("accountant", "admin")
def registry():
    query = _apply_filters(_base_query())
    documents = query.order_by(Document.uploaded_at.desc()).all()
    drivers = User.query.filter_by(role="driver").order_by(User.full_name).all()
    return render_template(
        "accountant/registry.html",
        documents=documents,
        drivers=drivers,
        statuses=DocumentStatus,
        active_filters=request.args,
    )


@accountant_bp.get("/document/<int:doc_id>")
@login_required
@role_required("accountant", "admin")
def document_details(doc_id: int):
    doc = Document.query.get_or_404(doc_id)
    return jsonify(
        {
            "id": doc.id,
            "image_url": url_for("accountant.upload_file", filename=doc.file_name),
            "order_number": doc.order_number,
            "document_type": doc.document_type,
            "status": doc.status,
            "status_comment": doc.status_comment or "",
            "driver": doc.driver.full_name,
            "uploaded_at": doc.uploaded_at.strftime("%d.%m.%Y %H:%M"),
            "doc_number": doc.doc_number or "",
            "doc_date": doc.doc_date.strftime("%d.%m.%Y") if doc.doc_date else "",
            "counterparty": doc.counterparty or "",
            "amount": doc.amount_display(),
            "ocr_available": doc.ocr_available,
            "quality": {
                "blur": round(doc.blur_metric or 0, 2),
                "brightness": round(doc.brightness_metric or 0, 2),
                "resolution": f"{doc.width}×{doc.height}" if doc.width and doc.height else "",
            },
        }
    )


@accountant_bp.route("/accept/<int:doc_id>", methods=["POST"])
@login_required
@role_required("accountant", "admin")
def accept_document(doc_id: int):
    doc = Document.query.get_or_404(doc_id)
    doc.status = DocumentStatus.ACCEPTED.value
    doc.status_comment = None
    doc.reviewed_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("accountant.registry", **request.args.to_dict()))


@accountant_bp.route("/reject/<int:doc_id>", methods=["POST"])
@login_required
@role_required("accountant", "admin")
def reject_document(doc_id: int):
    doc = Document.query.get_or_404(doc_id)
    reason = request.form.get("reason", "").strip()
    comment = request.form.get("comment", "").strip()
    doc.status = DocumentStatus.REJECTED.value
    doc.status_comment = f"{reason}. {comment}".strip(". ")
    doc.reviewed_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("accountant.registry", **request.args.to_dict()))


@accountant_bp.route("/exports/excel")
@login_required
@role_required("accountant", "admin")
def export_excel():
    documents = _apply_filters(_base_query()).order_by(Document.uploaded_at.desc()).all()
    filename = export_documents_to_excel(documents, export_folder=current_app.config["EXPORT_FOLDER"])
    return send_from_directory(current_app.config["EXPORT_FOLDER"], filename, as_attachment=True)


@accountant_bp.route("/uploads/<path:filename>")
@login_required
@role_required("accountant", "admin", "driver")
def upload_file(filename: str):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@accountant_bp.route("/1c")
@login_required
@role_required("accountant", "admin")
def one_c_page():
    docs = Document.query.filter_by(status=DocumentStatus.ACCEPTED.value).order_by(Document.uploaded_at.desc()).all()
    selected_id = request.args.get("doc_id", type=int)
    selected = next((doc for doc in docs if doc.id == selected_id), docs[0] if docs else None)
    return render_template("accountant/one_c.html", documents=docs, selected=selected)
