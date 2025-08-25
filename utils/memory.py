from datetime import datetime

class Memory:
    def __init__(self):
        # Very small in‑memory store keyed by session_id
        self.store = {}

    def get(self, session_id: str, key: str, default=None):
        return self.store.get(session_id, {}).get(key, default)

    def set(self, session_id: str, key: str, value):
        self.store.setdefault(session_id, {})[key] = value

    def ensure_session(self, session_id: str):
        self.store.setdefault(session_id, {"created_at": datetime.utcnow().isoformat()})
        return self.store[session_id]