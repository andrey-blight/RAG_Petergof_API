from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from API.app.core import validate_user
from API.app import create_review
from API.app import Review
from API.app.db.session import get_db

router = APIRouter(dependencies=[Depends(validate_user)])


@router.post("/review", status_code=200)
async def get_answer_from_rag(review: Review, db: AsyncSession = Depends(get_db)):
    await create_review(db, review)
    return 200
