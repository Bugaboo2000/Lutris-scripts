def enum_value_constrained_string(enum) -> str:
    v = enum.value
    assert isinstance(v, str)

    return v
