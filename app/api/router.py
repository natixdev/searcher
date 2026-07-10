from fastapi import APIRouter

from .v1 import documents_router, search_router


router = APIRouter(prefix='/api/v1')

router.include_router(search_router)
router.include_router(documents_router)
