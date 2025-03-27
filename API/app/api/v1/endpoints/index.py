from fastapi import APIRouter, Depends

from app.core.dependencies import validate_user, validate_admin_user
from rag import get_files as get_files_from_rag
from rag import get_indexes as get_indexes_from_rag
from app.db.schemas import FilesResponse, IndexesResponse

router = APIRouter(dependencies=[Depends(validate_user)])


@router.get("/files", status_code=200, response_model=FilesResponse,
            dependencies=[Depends(validate_admin_user)])
async def get_files():
    return FilesResponse(files=get_files_from_rag())


@router.get("/indexes", status_code=200, response_model=IndexesResponse)
async def get_indexes():
    return IndexesResponse(indexes=get_indexes_from_rag())
