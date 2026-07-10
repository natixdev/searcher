from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.schemas import DocumentResponse, SearchRequest, SearchResponse
from app.services import search_documents

router = APIRouter(prefix='/search', tags=['Search'])


@router.post('', response_model=SearchResponse)
async def search(
    request: SearchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SearchResponse:
    """Возвращает найденные документы."""
    documents = await search_documents(session=session, text=request.text)
    return SearchResponse(
        documents=[
            DocumentResponse.model_validate(document) for document in documents
        ],
    )
