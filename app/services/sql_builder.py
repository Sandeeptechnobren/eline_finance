def build_sql(intent: dict) -> str:
    if not intent.get("start_date") or not intent.get("end_date"):
        raise ValueError("Cannot generate SQL without a valid date range")

    if intent.get("multiple_categories"):
       
        if intent.get("percentage_change") is not None:
            raise ValueError(
                "Percentage change is not allowed for multiple categories"
            )

        keys = "', '".join(intent["categories"])

        if intent.get("aggregation") == "sum":
            select_clause = f"SUM(amount)  AS total_{intent['categories']}"
        elif intent.get("aggregation") == "avg":
            select_clause = f"AVG(amount) AS average_{intent['categories']}"
        else:
            raise ValueError(
                "Aggregation is required for multiple categories"
            )

        return f"""
SELECT
  {select_clause}
FROM forecasts
WHERE category_key IN ('{keys}')
  AND date >= CURRENT_DATE
  AND date BETWEEN '{intent["start_date"]}' AND '{intent["end_date"]}';
""".strip()


    if intent.get("aggregation") == "sum":
        select_clause = f"SUM(amount) AS total_{intent['category_key']}"
    elif intent.get("aggregation") == "avg":
        select_clause = f"AVG(amount) AS average_{intent['category_key']}"
    else:
        select_columns = ["date", "amount"]

        if intent.get("percentage_change") is not None:
            multiplier = 1 + (intent["percentage_change"] / 100)
            select_columns.append(
                f"amount * {multiplier} AS adjusted_amount"
            )

        select_clause = ",\n  ".join(select_columns)

    return f"""
SELECT
  {select_clause}
FROM forecasts
WHERE category_key = '{intent["category_key"]}'
  AND date >= CURRENT_DATE
  AND date BETWEEN '{intent["start_date"]}' AND '{intent["end_date"]}';
""".strip()
