from fastapi import APIRouter
from app.models.request import QueryRequest
from app.core.session import get_session, save_session
from app.services.nlp_service import analyze_input
from app.services.sql_builder import build_sql

router = APIRouter()


@router.post("/query")
async def query_builder(request: QueryRequest):
    session = get_session(request.sessionId)
    intent = analyze_input(request.input, session)

    print("Analyzed Intent:", intent)

    # 🔑 SINGLE source of clarification truth
    if intent.get("needs_clarification"):
        save_session(request.sessionId, intent)
        return {
            "sessionId": request.sessionId,
            "response_text": intent.get(
                "clarification_reason",
                "Please clarify your request."
            ),
            "status": "pending"
        }

    # Build SQL safely
    query = build_sql(intent)

    # -------------------------------------
    # Response text
    # -------------------------------------
    if intent.get("multiple_categories"):
        categories_text = ", ".join(
            c.replace("_", " ") for c in intent["categories"]
        )
        response_text = (
            f"Here is the total for {categories_text} "
            f"for the {intent.get('time_text') or 'selected period'}."
        )

    elif intent.get("aggregation") == "sum":
        response_text = (
            f"Here is the total {intent['category_key'].replace('_', ' ')} "
            f"for the {intent.get('time_text') or 'selected period'}."
        )

    elif intent.get("aggregation") == "avg":
        response_text = (
            f"Here is the average {intent['category_key'].replace('_', ' ')} "
            f"for the {intent.get('time_text') or 'selected period'}."
        )

    elif intent.get("percentage_change") is not None:
        direction = intent.get("change_direction", "increase")
        response_text = (
            f"This what-if scenario shows {intent['category_key'].replace('_', ' ')} "
            f"with a {intent['percentage_change']}% {direction} "
            f"applied for the {intent.get('time_text') or 'selected period'}."
        )

    else:
        response_text = (
            f"This query returns the forecasted "
            f"{intent['category_key'].replace('_', ' ')} "
            f"for the {intent.get('time_text') or 'selected period'}."
        )

    return {
        "sessionId": request.sessionId,
        "response_text": response_text,
        "query": query,
        "status": "finished"
    }
