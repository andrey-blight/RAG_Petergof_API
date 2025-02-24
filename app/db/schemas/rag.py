from pydantic import BaseModel


class RagResponse(BaseModel):
    answer: str


class RagQuestion(BaseModel):
    question: str
