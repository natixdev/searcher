from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.services import DocumentNotFoundError, delete_document


router = APIRouter(prefix='/documents', tags=['Documents'])


@router.delete('/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    document_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Обрабатывает запро на удаление документа по id."""
    try:
        await delete_document(session=session, document_id=document_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Документ не найден',
        ) from None
