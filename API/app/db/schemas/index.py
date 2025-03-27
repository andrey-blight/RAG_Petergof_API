from pydantic import BaseModel


class FilesResponse(BaseModel):
    files: list[str]

class IndexesResponse(BaseModel):
    indexes: list[str]

class RagQuestion(BaseModel):
    question: str
