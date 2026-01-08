import time

_SESSIONS = {}
SESSION_TTL = 60 * 30  # 30 minutes

def get_session(session_id: str):
    session = _SESSIONS.get(session_id)
    if not session:
        return {}
    if time.time() - session["updated_at"] > SESSION_TTL:
        _SESSIONS.pop(session_id, None)
        return {}
    return session["data"]

def save_session(session_id: str, data: dict):
    _SESSIONS[session_id] = {
        "data": data,
        "updated_at": time.time()
    }
