
from fastapi import FastAPI

from app.api import api_router


app = FastAPI(
    title='API для поиска текста в документах и удаления документов',
    description='Тестовое задание, Хуснутдинова Н.А.',
)


app.include_router(api_router)
