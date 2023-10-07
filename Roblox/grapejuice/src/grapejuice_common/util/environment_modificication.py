import os
from typing import MutableMapping, Any, Dict


class EnvironmentModification:
    _variables: Dict[str, str]
    _to_restore: Dict[str, str]

    def __init__(self, variables: MutableMapping[str, Any]):
        self._variables = {k: str(v) for k, v in variables.items()}
        self._to_restore = {}

    def __enter__(self):
        for k, v in self._variables.items():
            if k in os.environ:
                self._to_restore[k] = os.environ[k]

            os.environ[k] = v

    def __exit__(self, exc_type, exc_val, exc_tb):
        for k, _ in self._variables.items():
            os.environ.pop(k, None)

        for k, v in self._to_restore.items():
            os.environ[k] = v
