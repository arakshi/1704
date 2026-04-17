document.addEventListener("DOMContentLoaded", () => {
    const modalEl = document.getElementById("docModal");
    if (!modalEl) return;

    const modal = new bootstrap.Modal(modalEl);
    const imageEl = document.getElementById("modalImage");
    const metaEl = document.getElementById("modalMeta");
    let zoom = 1;

    document.querySelectorAll(".clickable-doc").forEach((el) => {
        el.addEventListener("click", async (event) => {
            event.preventDefault();
            const docId = el.dataset.docId;
            if (!docId) return;

            const response = await fetch(`/accountant/document/${docId}`);
            if (!response.ok) return;
            const data = await response.json();

            imageEl.src = data.image_url;
            metaEl.innerHTML = `
                <p><strong>ID:</strong> ${data.id}</p>
                <p><strong>Заказ:</strong> ${data.order_number}</p>
                <p><strong>Тип:</strong> ${data.document_type}</p>
                <p><strong>Номер:</strong> ${data.doc_number || "-"}</p>
                <p><strong>Дата:</strong> ${data.doc_date || "-"}</p>
                <p><strong>Контрагент:</strong> ${data.counterparty || "-"}</p>
                <p><strong>Сумма:</strong> ${data.amount || "-"}</p>
                <p><strong>Статус:</strong> ${data.status}</p>
                <p><strong>Комментарий:</strong> ${data.status_comment || "-"}</p>
                <p><strong>Водитель:</strong> ${data.driver}</p>
                <hr>
                <p><strong>Blur:</strong> ${data.quality.blur}</p>
                <p><strong>Brightness:</strong> ${data.quality.brightness}</p>
                <p><strong>Resolution:</strong> ${data.quality.resolution}</p>
                <p><strong>OCR:</strong> ${data.ocr_available ? "доступен" : "недоступен"}</p>
            `;
            zoom = 1;
            imageEl.style.transform = `scale(${zoom})`;
            modal.show();
        });
    });

    document.getElementById("zoomIn")?.addEventListener("click", () => {
        zoom += 0.1;
        imageEl.style.transform = `scale(${zoom})`;
    });

    document.getElementById("zoomOut")?.addEventListener("click", () => {
        zoom = Math.max(0.2, zoom - 0.1);
        imageEl.style.transform = `scale(${zoom})`;
    });
});
