from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from PIL import Image
from werkzeug.utils import secure_filename

from app.models import Document, DocumentStatus, db
from app.routes.utils import login_required, role_required
from app.services.image_quality import evaluate_image_quality
from app.services.ocr_service import extract_document_data

driver_bp = Blueprint("driver", __name__, url_prefix="/driver")


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@driver_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
@role_required("driver")
def dashboard():
    if request.method == "POST":
        return _handle_upload()

    documents = (
        Document.query.filter_by(user_id=session["user_id"])
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return render_template("driver/dashboard.html", documents=documents, statuses=DocumentStatus)


@driver_bp.post("/reupload/<int:doc_id>")
@login_required
@role_required("driver")
def reupload(doc_id: int):
    existing = Document.query.filter_by(id=doc_id, user_id=session["user_id"]).first_or_404()
    if existing.status not in {DocumentStatus.REJECTED.value, DocumentStatus.NEED_REUPLOAD.value, DocumentStatus.AUTO_REJECTED.value}:
        flash("Этот документ нельзя перезагрузить.", "warning")
        return redirect(url_for("driver.dashboard"))
    return _handle_upload(existing.order_number, existing.document_type)


def _handle_upload(order_number_prefill: str | None = None, doc_type_prefill: str | None = None):
    order_number = request.form.get("order_number", order_number_prefill or "").strip()
    document_type = request.form.get("document_type", doc_type_prefill or "").strip()
    uploaded_file = request.files.get("file")

    if not order_number or not document_type or not uploaded_file:
        flash("Заполните номер заказа, тип документа и выберите файл.", "danger")
        return redirect(url_for("driver.dashboard"))

    if not _allowed_file(uploaded_file.filename):
        flash("Разрешены только изображения: png, jpg, jpeg, webp, bmp, tif, tiff.", "danger")
        return redirect(url_for("driver.dashboard"))

    safe_name = secure_filename(uploaded_file.filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    stored_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}.{ext}"
    file_path = Path(current_app.config["UPLOAD_FOLDER"]) / stored_name

    try:
        image = Image.open(uploaded_file.stream)
        image = image.convert("RGB")
        file_path = file_path.with_suffix(".jpg")
        stored_name = file_path.name
        image.save(file_path, format="JPEG", quality=92)
    except Exception:  # noqa: BLE001
        uploaded_file.stream.seek(0)
        uploaded_file.save(file_path)

    quality = evaluate_image_quality(str(file_path))
    ocr_data = extract_document_data(str(file_path), current_app.config.get("TESSERACT_CMD", ""))

    status = quality.status if not quality.is_ok else DocumentStatus.UNDER_REVIEW.value
    status_comment = quality.message if not quality.is_ok else None

    document = Document(
        order_number=order_number,
        document_type=document_type,
        file_name=file_path.name,
        original_name=safe_name,
        status=status,
        status_comment=status_comment,
        ocr_available=ocr_data["ocr_available"],
        ocr_text=ocr_data.get("ocr_text"),
        doc_number=ocr_data.get("doc_number"),
        doc_date=ocr_data.get("doc_date"),
        amount=ocr_data.get("amount"),
        counterparty=ocr_data.get("counterparty"),
        blur_metric=quality.blur_metric,
        brightness_metric=quality.brightness_metric,
        width=quality.width,
        height=quality.height,
        quality_score=quality.score,
        user_id=session["user_id"],
    )

    db.session.add(document)
    db.session.commit()

    if not quality.is_ok:
        flash(quality.message, "warning")
    else:
        flash("Документ успешно загружен и отправлен на проверку.", "success")

    if not ocr_data["ocr_available"]:
        flash(ocr_data["ocr_message"], "info")

    return redirect(url_for("driver.dashboard"))
