# Поисковик по документам (тестовое)

Простой поисковик по текстам документов

## Стек

* Python 3.13
* FastAPI
* PostgreSQL
* Elasticsearch
* SQLAlchemy 2.0
* Alembic
* Docker Compose

## Функциональность

### Поиск документов

```
POST /api/v1/search
```

Принимает текст запроса, выполняет поиск в Elasticsearch, получает найденные идентификаторы документов и загружает полные данные из PostgreSQL.
Возвращает не более 20 документов со всем полями БД, упорядоченные по дате создания

### Удаление документа

```
DELETE /api/v1/documents/{document_id}
```

Удаляет документ из PostgreSQL и Elasticsearch

---

## Структура проекта

```
.
├── alembic/
├── app/
├── scripts/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── docs.json
└── README.md
```

---

## Запуск проекта

### 1. Клонировать репозиторий

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Добавить файл `posts.csv`

Файл `posts.csv` **не входит в репозиторий**, так как содержит закрытые данные.
После клонирования проекта необходимо вручную поместить файл `posts.csv` в корень проекта:

```text
.
├── posts.csv
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── ...
```

### 3. Создать файл `.env`

Скопируйте шаблон настроек:

```bash
cp .env.example .env
```

При необходимости измените значения переменных окружения в файле `.env`

### 4. Запустить приложение

```bash
docker compose up --build
```

При первом запуске автоматически выполняются:

* запуск PostgreSQL и Elasticsearch
* применение миграций Alembic
* импорт документов из `posts.csv`
* запуск FastAPI

После запуска сервис будет доступен по адресу:

```text
http://localhost:8000
```

---

## Документация API

Swagger UI:

```
http://localhost:8000/docs
```

OpenAPI:

```
http://localhost:8000/openapi.json
```

Файл `docs.json` в корне репозитория (по заданию, рядом с README.md)

---

## Пример поиска

### Запрос

```http
POST /api/v1/search
Content-Type: application/json
```

```json
{
  "text": "fastapi"
}
```

### Ответ

```json
{
  "documents": [
    {
      "id": 1,
      "rubrics": [
        "python"
      ],
      "text": "FastAPI is a modern Python framework.",
      "created_date": "2025-01-01T10:00:00"
    }
  ]
}
```

---

## Пример удаления

```http
DELETE /api/v1/documents/1
```

Ответ:

```
204 No Content
```

---

## Архитектура

* PostgreSQL хранит полные данные документов
* Elasticsearch используется только для поиска
* После поиска из Elasticsearch извлекаются идентификаторы документов
* Полные данные загружаются из PostgreSQL

---

## Особенности реализации

* Асинхронное взаимодействие с PostgreSQL и Elasticsearch
* Версионирование API (`/api/v1`)
* Управление схемой базы данных через Alembic
* Упрощенная архитектура для тестового
* PostgreSQL - источник истины
* При сбое удаления в Elasticsearch не возвращается ошибка 500, если был успешный коммит в PostgreSQL -- ошибка логируется
