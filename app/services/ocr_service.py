from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import cv2
import numpy as np
import pytesseract


def extract_document_data(file_path: str, tesseract_cmd: str = "") -> dict:
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return _empty(False, "OCR недоступен: файл изображения не удалось прочитать.")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang="rus+eng")
        parsed = _parse_text(text)
        parsed["ocr_available"] = True
        parsed["ocr_message"] = "OCR выполнен."
        return parsed
    except (pytesseract.TesseractNotFoundError, RuntimeError, FileNotFoundError):
        return _empty(False, "OCR недоступен: Tesseract не установлен или не найден.")
    except Exception as error:  # noqa: BLE001
        return _empty(False, f"OCR завершился с ошибкой: {error}")


def _empty(is_available: bool, message: str) -> dict:
    return {
        "ocr_available": is_available,
        "ocr_message": message,
        "ocr_text": "",
        "doc_number": None,
        "doc_date": None,
        "amount": None,
        "counterparty": None,
    }


def _parse_text(text: str) -> dict:
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    number_match = re.search(r"(?:№|N|No\.?|Номер)\s*([A-Za-zА-Яа-я0-9\-/]+)", cleaned)
    date_match = re.search(r"(\d{2}[./-]\d{2}[./-]\d{4})", cleaned)
    amount_match = re.search(r"(\d+[\d\s]*[.,]\d{2})", cleaned)

    counterparty = None
    for pattern in [r"(?:Контрагент|Поставщик|Получатель)[:\s]+(.+)", r"ООО\s+«?[^\n»]+»?"]:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            counterparty = match.group(1).strip() if match.groups() else match.group(0).strip()
            break

    doc_date = None
    if date_match:
        for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"]:
            try:
                doc_date = datetime.strptime(date_match.group(1), fmt).date()
                break
            except ValueError:
                continue

    amount = None
    if amount_match:
        normalized = amount_match.group(1).replace(" ", "").replace(",", ".")
        try:
            amount = Decimal(normalized)
        except InvalidOperation:
            amount = None

    return {
        "ocr_text": cleaned,
        "doc_number": number_match.group(1) if number_match else None,
        "doc_date": doc_date,
        "amount": amount,
        "counterparty": counterparty,
    }
