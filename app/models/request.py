from pydantic import BaseModel

class QueryRequest(BaseModel):
    sessionId: str
    input: str
