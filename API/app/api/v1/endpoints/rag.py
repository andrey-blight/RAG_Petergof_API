import asyncio
import threading

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import validate_user
from rag import get_answer, get_indexes
from app.db.schemas import TaskResponse, RagQuestion, StatusResponse

import time

router = APIRouter(dependencies=[Depends(validate_user)])

tasks = {}


@router.post("/answer", status_code=200, response_model=TaskResponse)
async def get_answer_from_rag(question_schema: RagQuestion):
    if question_schema.index not in get_indexes():
        raise HTTPException(status_code=404, detail="Index not found")

    task_id = str(time.time())
    tasks[task_id] = False

    def background_task():
        try:
            answer = asyncio.run(get_answer(question_schema.index, question_schema.question))
            tasks[task_id] = answer
        except Exception as e:
            tasks[task_id] = f"error: {str(e)}"

    thread = threading.Thread(target=background_task)
    thread.start()

    return TaskResponse(task_id=task_id)


@router.get("/answer/status/{task_id}", response_model=StatusResponse)
async def check_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    if not tasks[task_id]:
        raise HTTPException(status_code=404, detail="Still running")
    return StatusResponse(status=tasks[task_id])
