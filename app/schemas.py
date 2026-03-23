from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    session_id: str = Field(..., description="Client session identifier")
    question: str = Field(..., min_length=2, description="Customer query")


class AskResponse(BaseModel):
    answer: str
    model: str
    session_id: str
