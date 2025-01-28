from fastapi import APIRouter

from rag import get_answer
from app.db.schemas import RagResponse, RagQuestion

# router = APIRouter(dependencies=[Depends(check_token)])
router = APIRouter()


@router.post("/answer", status_code=200, response_model=RagResponse)
async def get_answer_from_rag(question_schema: RagQuestion):
    return RagResponse(answer=await get_answer(question_schema.question))
