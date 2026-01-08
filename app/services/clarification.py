def needs_clarification(intent: dict) -> bool:
    if intent.get("aggregation") and intent.get("category_key"):
        return False
    return (
        intent.get("ambiguous_category", True)
        or not intent.get("start_date")
        or not intent.get("end_date")
    )

def clarification_question(intent: dict) -> str:
    if intent.get("clarification_reason"):
        return intent["clarification_reason"]
    if intent.get("ambiguous_category"):
        return "Which category do you mean?"
    if not intent.get("start_date"):
        return "Please specify the time period."
    return "Please clarify your request."
