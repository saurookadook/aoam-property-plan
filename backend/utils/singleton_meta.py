from __future__ import annotations

import threading


class SingletonMeta(type):
    """A metaclass that creates a Singleton instance of the decorated class.

    Partially inspired by implementation here:
    - https://gist.github.com/werediver/4396488
    """

    _instances = {}
    __singleton_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls.__singleton_lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
