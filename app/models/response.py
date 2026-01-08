from pydantic import BaseModel
from typing import Optional

class QueryResponse(BaseModel):
    sessionId: str
    response_text: str
    status: str
    query: Optional[str] = None
