from fastapi import APIRouter, Depends

from API.app.core import validate_user
from rag import get_answer
from API.app import RagResponse, RagQuestion

router = APIRouter(dependencies=[Depends(validate_user)])


@router.post("/answer", status_code=200, response_model=RagResponse)
async def get_answer_from_rag(question_schema: RagQuestion):
    return RagResponse(answer=await get_answer("new", question_schema.question))
