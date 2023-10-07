import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class VenvBreakoutResult:
    env_snapshot: Optional[Dict[str, Any]]
    log: logging.Logger

    def restore_env_snapshot(self):
        if self.env_snapshot is not None:
            self.log.info("Restoring environment snapshot...")
            for env_key, env_value in self.env_snapshot.items():
                os.environ[env_key] = env_value


def break_out_of_virtualenv(log: logging.Logger) -> VenvBreakoutResult:
    env_snapshot = None

    if "VIRTUAL_ENV" in os.environ:
        virtual_env = os.environ["VIRTUAL_ENV"]
        log.warning(f"Breaking out of virtualenv: {virtual_env}")
        env_snapshot = dict(os.environ)

        path = os.environ["PATH"].split(os.pathsep)
        path = list(filter(lambda s: not s.startswith(virtual_env), path))
        os.environ["PATH"] = os.pathsep.join(path)

        log.info("Set PATH to: " + os.environ["PATH"])
        os.environ.pop("VIRTUAL_ENV", None)

    return VenvBreakoutResult(env_snapshot, log)


class VirtualEnv:
    _path: Path

    def __init__(self, path: Path):
        self._path = path

        if not self._path.is_absolute():
            raise RuntimeError(f"You must provide an absolute venv path. You provided: {self._path}")

    @property
    def exists(self):
        return self._path.exists() and self._path.is_dir()

    @property
    def python_bin_path(self):
        return self._path / "bin" / "python"

    def refresh(self):
        if self._path.exists():
            if self._path.is_file():
                os.remove(self._path)

            else:
                shutil.rmtree(self._path)

        subprocess.check_call(["virtualenv", "-p", sys.executable, str(self._path)])
