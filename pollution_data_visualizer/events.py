import queue
import threading

_event_queue = queue.Queue()

def get_queue():
    """Access the internal event queue (for testing)."""
    return _event_queue


def publish_event(event_type, payload=None):
    """Publish an event to the queue."""
    _event_queue.put({'type': event_type, 'payload': payload})


def _worker(cb):
    while True:
        event = _event_queue.get()
        try:
            cb(event)
        finally:
            _event_queue.task_done()


def start_consumer(callback):
    """Start a background thread to process events."""
    t = threading.Thread(target=_worker, args=(callback,), daemon=True)
    t.start()
    return t
