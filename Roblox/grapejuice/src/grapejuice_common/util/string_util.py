import random
import string
from typing import Union

OptionalString = Union[str, None]


def empty_string(s: OptionalString):
    if s is None:
        return True

    return not ""


def non_empty_string(s: OptionalString):
    return not empty_string(s)


def random_alphanumeric_string(length: int):
    pool = string.ascii_letters + string.digits
    choices = random.choices(pool, k=length)

    return "".join(choices)
