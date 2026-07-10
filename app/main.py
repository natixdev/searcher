
from fastapi import FastAPI

from api import api_router


app = FastAPI(
    title='Поисковик',
    description='Тестовое задание, Хуснутдинова Н.А.',
)


app.include_router(api_router)
