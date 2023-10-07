import os
import subprocess
import sys
import tarfile
from pathlib import Path
from string import Template

from setuptools import Command

import grapejuice_packaging.packaging_resources as res
from grapejuice_common import paths
from grapejuice_packaging.util.task_sequence import TaskSequence
from grapejuice_packaging.util.venv_util import break_out_of_virtualenv, VirtualEnv

PYTHON_INTERPRETER = sys.executable

ROBLOX_STUDIO = "roblox-studio.desktop"
ROBLOX_PLAYER = "roblox-player.desktop"
ROBLOX_STUDIO_AUTH = "roblox-studio-auth.desktop"

MIME = {
    "x-scheme-handler/roblox-studio": ROBLOX_STUDIO,
    "x-scheme-handler/roblox-player": ROBLOX_PLAYER,
    "x-scheme-handler/roblox-studio-auth": ROBLOX_STUDIO_AUTH,
    "x-scheme-handler/roblox": ROBLOX_PLAYER,
    "application/x-roblox-rbxl": ROBLOX_STUDIO,
    "application/x-roblox-rbxlx": ROBLOX_STUDIO
}


def _xdg_mime_default(desktop_entry: str, mime: str):
    subprocess.check_call(["xdg-mime", "default", desktop_entry, mime])


def _do_install(*_):
    assert os.path.exists("setup.py"), \
        "Project file not found, make sure you're in the Grapejuice root!"

    src_path = os.path.join(os.path.abspath(os.getcwd()), "src")
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] = src_path + ":" + os.environ["PYTHONPATH"]

    else:
        os.environ["PYTHONPATH"] = src_path

    install = TaskSequence("Install Grapejuice locally")

    @install.task("Build package of supplemental files")
    def build_supplemental(_log):
        subprocess.check_call([
            PYTHON_INTERPRETER, "-m", "grapejuice_packaging",
            "supplemental_package"
        ])

    @install.task("Install supplemental packages")
    def install_supplemental_packages(log):
        for file in Path("dist", "supplemental_package").glob("*.tar.gz"):
            log.info(f"Installing supplemental package {file}")

            with tarfile.open(file) as tar:
                tar.extractall(paths.home())

    @install.task("Install Grapejuice package")
    def install_package(log):
        breakout_result = break_out_of_virtualenv(log)

        venv = VirtualEnv(paths.grapejuice_venv())
        venv.refresh()

        pyproject_path = Path("./pyproject.toml").resolve()
        assert pyproject_path.exists(), \
            "Could not find pyproject.toml, make sure you are in the Grapejuice source root!"

        subprocess.check_call([
            str(venv.python_bin_path), "-m", "pip",
            "install", str(pyproject_path.parent),
            "--upgrade"
        ])

        def install_entrypoint(template_path: str, bin_path: Path):
            with open(template_path, "r", encoding=sys.getdefaultencoding()) as fp:
                template = Template(fp.read())

            entrypoint_string = template.safe_substitute({
                "_VIRTUALENV": str(paths.grapejuice_venv())
            })

            bin_path.parent.mkdir(parents=True, exist_ok=True)
            with bin_path.open("w+") as fp:
                fp.write(entrypoint_string)

            bin_path.chmod(0o775)

        install_entrypoint(res.local_bin_grapejuice_path(), paths.local_bin() / "grapejuice")
        install_entrypoint(res.local_bin_grapejuice_gui_path(), paths.local_bin() / "grapejuice-gui")

        breakout_result.restore_env_snapshot()

    @install.task("Updating GTK icon cache")
    def update_icon_cache(_log):
        subprocess.check_call(["gtk-update-icon-cache"])

    @install.task("Updating desktop database")
    def update_desktop_database(log):
        path = (paths.home() / ".local" / "share" / "applications").resolve()
        log.info(f"Updating desktop database: {path}")

        subprocess.check_call(["update-desktop-database", str(path)])

    @install.task("Updating MIME type associations")
    def update_mime_associations(log):
        for mime, desktop in MIME.items():
            log.info(f"Associating {mime} with {desktop}")
            _xdg_mime_default(desktop, mime)

    @install.task("Updating MIME database")
    def update_mime_database(log):
        path = (paths.home() / ".local" / "share" / "mime").resolve()
        log.info(f"Updating MIME database: {path}")

        subprocess.check_call(["update-mime-database", str(path)])

    install.run()


class InstallLocally(Command):
    description = "Install Grapejuice locally"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        _do_install(self.user_options)
