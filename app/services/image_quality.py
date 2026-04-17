from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class QualityResult:
    is_ok: bool
    message: str
    status: str
    blur_metric: float
    brightness_metric: float
    width: int
    height: int
    score: float


def evaluate_image_quality(file_path: str) -> QualityResult:
    image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return QualityResult(
            is_ok=False,
            message="Файл не распознан как изображение.",
            status="Отклонено автоматически",
            blur_metric=0,
            brightness_metric=0,
            width=0,
            height=0,
            score=0,
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_metric = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness_metric = float(gray.mean())
    height, width = gray.shape

    issues: list[str] = []
    status = "На проверке"

    if width < 1000 or height < 700:
        issues.append("низкое разрешение")
    if blur_metric < 80:
        issues.append("изображение размыто")
    if brightness_metric < 45:
        issues.append("изображение слишком темное")

    if len(issues) >= 2:
        status = "Отклонено автоматически"
    elif len(issues) == 1:
        status = "Требует повторной загрузки"

    if issues:
        return QualityResult(
            is_ok=False,
            message=f"Качество файла недостаточное: {', '.join(issues)}.",
            status=status,
            blur_metric=blur_metric,
            brightness_metric=brightness_metric,
            width=width,
            height=height,
            score=max(0, 100 - len(issues) * 35),
        )

    return QualityResult(
        is_ok=True,
        message="Изображение прошло автоматическую проверку качества.",
        status="На проверке",
        blur_metric=blur_metric,
        brightness_metric=brightness_metric,
        width=width,
        height=height,
        score=100,
    )
