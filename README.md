# Локальный проект для PyCharm: ООО «Лик Транс»

Веб-приложение для оперативного сбора сканов ТТН/актов, их проверки, OCR-обработки и работы бухгалтера с реестром.

## Стек
- Python 3.11+
- Flask
- SQLite
- SQLAlchemy
- Jinja2
- Bootstrap 5
- Pillow
- OpenCV
- pytesseract
- openpyxl
- python-dotenv

## Структура

```text
app/
  __init__.py
  config.py
  models.py
  routes/
  services/
  templates/
  static/
uploads/
exports/
instance/
main.py
requirements.txt
.env.example
README.md
```

## Запуск в PyCharm (максимально просто)
1. Откройте папку проекта в PyCharm.
2. Создайте виртуальное окружение (Python 3.11+):
   - `File -> Settings -> Project -> Python Interpreter -> Add Interpreter -> Virtualenv`
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. (Опционально) создайте `.env` на основе `.env.example`.
5. Запустите `main.py` (Run).
6. Откройте в браузере `http://127.0.0.1:5000`.

## Что создается автоматически
При первом запуске:
- папки `uploads/`, `exports/`, `instance/`;
- SQLite БД `instance/app.db`;
- demo-пользователи.

## Demo-логины
- `driver / 123456`
- `accountant / 123456`
- `admin / 123456`

## Где что хранится
- Загруженные сканы: `uploads/`
- Excel-выгрузки: `exports/`
- База SQLite: `instance/app.db`

## OCR и Tesseract
Приложение не падает, если Tesseract не установлен:
- документ сохраняется,
- OCR-поля остаются пустыми,
- показывается уведомление о недоступности OCR.

Если Tesseract установлен не в PATH, укажите путь в `.env`:
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Ключевые разделы
- Водитель: загрузка и история документов, статусы, перезагрузка отклоненных.
- Бухгалтер: реестр, фильтры, поиск, принятие/отклонение с комментарием, popup просмотр, экспорт в Excel.
- 1С (демо): упрощенный интерфейс просмотра принятых документов.
- Админка: пользователи, документы, создание demo-данных, сброс БД, переинициализация.

## Важно по ошибке SQLite `unable to open database file`
Если вы запускаете проект из нестандартной рабочей директории (частая ситуация в PyCharm),
приложение автоматически нормализует путь к SQLite в абсолютный путь от корня проекта.
Дополнительно можно явно прописать в `.env`:
```env
DATABASE_URL=sqlite:///instance/app.db
```
(путь будет автоматически приведен к абсолютному внутри проекта).
