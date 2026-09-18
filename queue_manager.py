"""
Har group ke liye alag gaana queue rakhta hai.
"""

queues: dict[int, list[dict]] = {}


def add_to_queue(chat_id: int, song: dict):
    queues.setdefault(chat_id, []).append(song)


def get_queue(chat_id: int) -> list[dict]:
    return queues.get(chat_id, [])


def pop_next(chat_id: int):
    """Current gaana hata kar agla gaana return karta hai (ya None)."""
    q = queues.get(chat_id, [])
    if q:
        q.pop(0)
    if q:
        return q[0]
    return None


def current_song(chat_id: int):
    q = queues.get(chat_id, [])
    return q[0] if q else None


def clear_queue(chat_id: int):
    queues[chat_id] = []
