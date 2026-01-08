import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

FY_START_MONTH = 4  # April (India FY)

def _quarter_range(year: int, quarter: int):
    start_month = (quarter - 1) * 3 + 1
    start = date(year, start_month, 1)

    if start_month + 3 > 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, start_month + 3, 1) - timedelta(days=1)

    return start, end


def _financial_year_range(year: int):
    start = date(year, FY_START_MONTH, 1)
    end = date(year + 1, FY_START_MONTH, 1) - timedelta(days=1)
    return start, end


def extract_date_range(text: str | None):
    if not text:
        return None, None

    text = text.lower()
    today = date.today()
    year = today.year

    if "today" in text:
        return str(today), str(today)

    if "tomorrow" in text:
        d = today + timedelta(days=1)
        return str(d), str(d)

    if "this week" in text:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return str(start), str(end)

    if "last week" in text:
        this_week_start = today - timedelta(days=today.weekday())
        start = this_week_start - timedelta(days=7)
        end = this_week_start - timedelta(days=1)
        return str(start), str(end)

    if "next week" in text:
        start = today - timedelta(days=today.weekday()) + timedelta(days=7)
        end = start + timedelta(days=6)
        return str(start), str(end)

    match = re.search(r"next\s+(\d+)\s+months?", text)
    if match:
        n = int(match.group(1))
        start = today
        end = today + relativedelta(months=n)
        return str(start), str(end)

    match = re.search(r"(last|previous)(?:\s+(\d+))?\s+months?", text)
    if match:
        n = int(match.group(2)) if match.group(2) else 1
        end = today
        start = today - relativedelta(months=n)
        return str(start), str(end)

    if "ytd" in text or "year to date" in text:
        return date(year, 1, 1), today

    if "quarter" in text:
        current_quarter = (today.month - 1) // 3 + 1

        if "next" in text:
            q = current_quarter + 1
            y = year
            if q == 5:
                q = 1
                y += 1
            return _quarter_range(y, q)

        if "last" in text or "previous" in text:
            q = current_quarter - 1
            y = year
            if q == 0:
                q = 4
                y -= 1
            return _quarter_range(y, q)

        if "this" in text:
            return _quarter_range(year, current_quarter)

    match = re.search(r"q([1-4])(?:\s*(\d{4}))?", text)
    if match:
        q = int(match.group(1))
        y = int(match.group(2)) if match.group(2) else year
        return _quarter_range(y, q)


    if "fy" in text or "financial year" in text:
        if "next" in text:
            return _financial_year_range(year + 1)
        if "last" in text or "previous" in text:
            return _financial_year_range(year - 1)

        match = re.search(r"(fy|financial year)\s*(\d{4})", text)
        if match:
            return _financial_year_range(int(match.group(2)))

        if "this" in text:
            if today.month < FY_START_MONTH:
                return _financial_year_range(year - 1)
            return _financial_year_range(year)


    if "year" in text:
        if "next" in text:
            return date(year + 1, 1, 1), date(year + 1, 12, 31)
        if "last" in text or "previous" in text:
            return date(year - 1, 1, 1), date(year - 1, 12, 31)
        if "this" in text:
            return date(year, 1, 1), date(year, 12, 31)


    if "this month" in text:
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return start, end

    if "last month" in text or "previous month" in text:
        end = today.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
        return str(start), str(end)

    if "next month" in text:
        start = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return start, end

    return None, None
