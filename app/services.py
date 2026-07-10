import logging

from elasticsearch import NotFoundError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.elastic import elasticsearch_client
from app.models import Document
from app.settings import settings


logger = logging.getLogger(__name__)


class DocumentNotFoundError(Exception):
    """Документ не найден."""


async def index_document(document: Document) -> None:
    """Индексирует документ в Elasticsearch."""
    try:
        await elasticsearch_client.index(
            index=settings.elasticsearch_index,
            id=document.id,
            document={
                'id': document.id,
                'text': document.text,
            },
        )
    except Exception:
        logger.exception(
            'Ошибка при индексировании документа с id = %s.', document.id
        )
        raise


async def search_documents(
    session: AsyncSession,
    text: str,
) -> list[Document]:
    """Выполняет поиск документов."""
    response = await elasticsearch_client.search(
        index=settings.elasticsearch_index,
        size=20,
        query={
            'match': {
                'text': text,
            },
        },
    )

    document_ids = [
        int(hit['_source']['id']) for hit in response['hits']['hits']
    ]
    if not document_ids:
        return []

    result = await session.execute(
        select(Document)
        .where(Document.id.in_(document_ids))
        .order_by(Document.created_date.desc())
    )
    return result.scalars().all()


async def delete_document(
    session: AsyncSession,
    document_id: int,
) -> None:
    """Удаляет документ из PostgreSQL и Elasticsearch."""
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise DocumentNotFoundError

    await session.delete(document)
    await session.commit()

    try:
        await elasticsearch_client.delete(
            index=settings.elasticsearch_index,
            id=document_id,
        )
    except NotFoundError:
        logger.warning(
            'Документ с id = %s не найде в Elasticsearch', document_id,
        )
    except Exception:
        logger.exception(
            'Ошибка при удалении документа с id = %s',
            document_id,
        )
        raise
