def format_response(intent: dict) -> str:
    time_text = intent.get("time_text", "the selected period")

    if intent.get("multiple_categories"):
        categories = ", ".join(
            c.replace("_", " ") for c in intent["categories"]
        )
        return f"Here is the combined total of {categories} for {time_text}."

    if intent.get("percentage_change") is not None:
        direction = intent.get("change_direction", "increase")
        return (
            f"This what-if scenario shows "
            f"{intent['category_key'].replace('_', ' ')} "
            f"with a {intent['percentage_change']}% {direction} "
            f"applied for {time_text}."
        )

    if intent.get("aggregation") == "sum":
        return (
            f"Here is the total "
            f"{intent['category_key'].replace('_', ' ')} "
            f"for {time_text}."
        )

    if intent.get("aggregation") == "avg":
        return (
            f"Here is the average "
            f"{intent['category_key'].replace('_', ' ')} "
            f"for {time_text}."
        )

    return (
        f"Here is the forecast of "
        f"{intent['category_key'].replace('_', ' ')} "
        f"for {time_text}."
    )
