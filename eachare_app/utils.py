import threading

def print_with_lock(*args, **kwargs):
    if not hasattr(print_with_lock, "_lock"):
        print_with_lock._lock = threading.Lock()
    with print_with_lock._lock:
        print(*args, **kwargs)
