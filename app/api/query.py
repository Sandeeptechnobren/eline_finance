from fastapi import APIRouter
from app.models.request import QueryRequest
from app.core.session import get_session, save_session
from app.services.nlp_service import analyze_input
from app.services.sql_builder import build_sql
from app.utils.text_normalizer import format_response

router = APIRouter()


@router.post("/query")
async def query_builder(request: QueryRequest):
    session = get_session(request.sessionId)
    intent = analyze_input(request.input, session)

  

    if intent.get("needs_clarification") or (
    not intent.get("multiple_categories") and not intent.get("category_key")):
        save_session(request.sessionId, intent)
        return {
            "sessionId": request.sessionId,
            "response_text": intent.get(
                "clarification_reason",
                "Please clarify your request."
            ),
            "status": "pending"
        }


    query = build_sql(intent)



    return {
        "sessionId": request.sessionId,
        "response_text": format_response(intent),
        "query": query,
        "status": "finished"
    }
