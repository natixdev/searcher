# scripts/import_documents.py
import argparse
import ast
import asyncio
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import async_session, engine
from app.elastic import elasticsearch_client
from app.models import Document
from app.settings import settings
from app.db import Base


async def init_db():
    """Создаёт таблицы, если их нет."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def import_documents(csv_file: Path) -> None:
    """Импортирует документы из CSV."""
    documents: list[Document] = []

    with csv_file.open(
        mode='r',
        encoding='utf-8',
        newline='',
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            document = Document(
                text=row['text'],
                rubrics=ast.literal_eval(row['rubrics']),
                created_date=datetime.fromisoformat(
                    row['created_date'],
                ),
            )
            documents.append(document)

    async with async_session() as session:
        session.add_all(documents)
        await session.flush()
        await session.commit()

        for document in documents:
            await elasticsearch_client.index(
                index=settings.elasticsearch_index,
                id=document.id,
                document={
                    'id': document.id,
                    'text': document.text,
                },
            )

    print(f'Imported {len(documents)} documents.')

async def main() -> None:
    """Точка входа."""
    args = parse_arguments()
    
    # Создаём таблицы
    await init_db()
    
    try:
        await import_documents(args.csv_file)
    finally:
        # Закрываем клиент Elasticsearch
        await elasticsearch_client.close()
        print("Elasticsearch client closed.")

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Импорт документов в PostgreSQL и Elasticsearch.',
    )
    parser.add_argument(
        'csv_file',
        type=Path,
        help='Путь к CSV-файлу с документами.',
    )
    return parser.parse_args()

if __name__ == '__main__':
    asyncio.run(main())
