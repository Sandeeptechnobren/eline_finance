import json
from app.services.llm_client import call_llm
from app.core.s3_loader import load_categories
from app.services.category_resolver import resolve_category
from app.utils.date_parser import extract_date_range

CATEGORIES = load_categories()



# Aggregation detector (from USER input only)
def detect_aggregation(text: str):
    text = text.lower()
    if "total" in text or "sum" in text:
        return "sum"
    if "average" in text or "avg" in text:
        return "avg"
    return None

def get_category_type(category_key: str, categories: dict):
    for cat_type, group in categories.items():
        if category_key in group:
            return cat_type
    return None


def analyze_input(user_input: str, session: dict):
    llm_raw = call_llm(user_input, session)

    try:
        llm_data = json.loads(llm_raw)
    except json.JSONDecodeError:
        return {
            "needs_clarification": True,
            "clarification_reason": "Could not understand the request.",
        }


    intent = session.copy() if session else {}

    intent["raw_input"] = user_input
    intent["llm"] = llm_data

    intent["aggregation"] = detect_aggregation(user_input)

    label = llm_data.get("category_label")

    if label:
        matches = resolve_category(label, CATEGORIES)
    else:
        matches = []
        
    if not matches:
        matches = resolve_category(user_input, CATEGORIES)


    intent["categories"] = matches
    intent["multiple_categories"] = len(matches) > 1
    intent["ambiguous_category"] = len(matches) == 0

    if not intent["multiple_categories"] and matches:
        intent["category_key"] = matches[0]


    if not intent["categories"]:
        intent["needs_clarification"] = True
        intent["clarification_reason"] = (
            "Please specify which category you want "
            "(for example: Operating income, New income)."
        )
        return intent   

    if intent["multiple_categories"]:
        types = {
            get_category_type(key, CATEGORIES)
            for key in matches
        }

        if len(types) > 1:
            intent["needs_clarification"] = True
            intent["clarification_reason"] = (
                "Please select categories of the same type "
                "(income or expense)."
            )
            return intent

        if not intent.get("aggregation"):
            intent["needs_clarification"] = True
            intent["clarification_reason"] = (
                "Please specify how you want to combine these categories "
                "(for example: total)."
            )
            return intent

        if llm_data.get("percentage_change") is not None:
            intent["needs_clarification"] = True
            intent["clarification_reason"] = (
                "What-if percentage scenarios can only be applied to one "
                "category at a time."
            )
            return intent


    llm_time = llm_data.get("normalized_time_expression")
    time_expr = llm_data.get("time_expression")
    start, end = extract_date_range(llm_time or time_expr or user_input)

    intent["start_date"] = str(start) if start else None
    intent["end_date"] = str(end) if end else None

    if llm_data.get("normalized_time_expression"):
        intent["time_text"] = llm_data["normalized_time_expression"]
    elif llm_data.get("time_expression"):
        intent["time_text"] = llm_data["time_expression"]
    elif start and end:
        intent["time_text"] = f"between {start} and {end}"
    else:
        intent["time_text"] = None


    if llm_data.get("percentage_change") is not None:
        intent["percentage_change"] = llm_data["percentage_change"]
    else:
        intent.pop("percentage_change", None)

    intent["change_direction"] = llm_data.get("change_direction")

    missing_time = not start or not end

    intent["needs_clarification"] = (
        missing_time
        or (
            not intent.get("aggregation")
            and (
                llm_data.get("needs_clarification")
                or intent["ambiguous_category"]
            )
        )
    )

    if intent["needs_clarification"]:
        if missing_time:
            intent["clarification_reason"] = (
                f"Please specify the time period for which you want the "
                f"{intent.get('category_key', 'selected category')}."
            )
        else:
            intent["clarification_reason"] = llm_data.get(
                "clarification_reason",
                "Please clarify your request."
            )
    else:
        intent.pop("clarification_reason", None)

    return intent
