import asyncio

from fastapi import APIRouter, Depends, UploadFile, HTTPException

from app.core.dependencies import validate_user, validate_admin_user
from rag import get_files as get_files_from_rag
from rag import get_indexes as get_indexes_from_rag
from ocr import ApiOCR
from app.db.schemas import FilesResponse, IndexesResponse, OcrStatusResponse

router = APIRouter(dependencies=[Depends(validate_user)])
ocr = ApiOCR()


@router.get("/files", status_code=200, response_model=FilesResponse,
            dependencies=[Depends(validate_admin_user)])
async def get_files():
    return FilesResponse(files=get_files_from_rag())


@router.get("/indexes", status_code=200, response_model=IndexesResponse)
async def get_indexes():
    return IndexesResponse(indexes=get_indexes_from_rag())


@router.post("/files", dependencies=[Depends(validate_admin_user)])
async def push_to_ocr(file: UploadFile):
    if file.filename in get_files_from_rag():
        raise HTTPException(status_code=409, detail="File already uploaded")
    if await ocr.is_running():
        return HTTPException(status_code=409, detail="OCR already running")
    content = await file.read()
    asyncio.create_task(ocr.upload_pdf(content, file.filename[:-4]))
    return 200


@router.get("/files/status", dependencies=[Depends(validate_admin_user)],
            response_model=OcrStatusResponse)
async def get_ocr_status():
    return OcrStatusResponse(is_running=await ocr.is_running())
