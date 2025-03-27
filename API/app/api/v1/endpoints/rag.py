from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import validate_user
from rag import get_answer, get_indexes
from app.db.schemas import RagResponse, RagQuestion

router = APIRouter(dependencies=[Depends(validate_user)])


@router.post("/answer", status_code=200, response_model=RagResponse)
async def get_answer_from_rag(question_schema: RagQuestion):
    if question_schema.index not in get_indexes():
        raise HTTPException(status_code=404, detail="Index not found")
    return RagResponse(answer=await get_answer(question_schema.index, question_schema.question))
