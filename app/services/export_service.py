from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font


def export_documents_to_excel(documents, export_folder: str) -> str:
    Path(export_folder).mkdir(parents=True, exist_ok=True)
    filename = f"registry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    full_path = Path(export_folder) / filename

    wb = Workbook()
    ws = wb.active
    ws.title = "Реестр документов"

    headers = [
        "ID",
        "Заказ",
        "Тип",
        "Номер документа",
        "Дата документа",
        "Контрагент",
        "Сумма",
        "Статус",
        "Водитель",
        "Дата загрузки",
    ]

    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for doc in documents:
        ws.append(
            [
                doc.id,
                doc.order_number,
                doc.document_type,
                doc.doc_number or "",
                doc.doc_date.strftime("%d.%m.%Y") if doc.doc_date else "",
                doc.counterparty or "",
                float(doc.amount) if doc.amount is not None else "",
                doc.status,
                doc.driver.full_name,
                doc.uploaded_at.strftime("%d.%m.%Y %H:%M"),
            ]
        )

    widths = [8, 16, 16, 22, 16, 26, 12, 20, 20, 20]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + idx)].width = width

    wb.save(full_path)
    return filename
