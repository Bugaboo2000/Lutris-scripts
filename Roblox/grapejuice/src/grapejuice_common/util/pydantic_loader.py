try:
    # Load Pydantic v1 from Pydantic v2.
    from pydantic import v1
    pydantic_v1 = v1
except ImportError:
    # Load Pydantic v1
    import pydantic
    pydantic_v1 = pydantic
