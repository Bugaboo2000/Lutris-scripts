import json
from functools import wraps
from typing import Optional, MutableMapping


def cache(cache_object: Optional[MutableMapping] = None):
    if cache_object is None:
        cache_object = dict()

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = hash(json.dumps({
                "fn": fn.__name__,
                "args": repr(args),
                "kwargs": repr(kwargs)
            }))
            cache_item = cache_object.get(cache_key, None)

            if cache_item is not None:
                return cache_item

            cache_item = fn(*args, **kwargs)
            cache_object[cache_key] = cache_item

            return cache_item

        return wrapper

    return decorator
