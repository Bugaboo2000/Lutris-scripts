import atexit
import json
import logging
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Union, List, Dict, Optional

from grapejuice_common import paths
from grapejuice_common.errors import HardwareProfilingError, WineHomeInvalid
from grapejuice_common.hardware_info.graphics_card import GPUVendor
from grapejuice_common.logs.log_util import log_function
from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel, ThirdPartyKeys
from grapejuice_common.util.string_util import non_empty_string
from grapejuice_common.wine.wineprefix_paths import WineprefixPaths

log = logging.getLogger(__name__)


class ProcessWrapper:
    on_exit: callable = None

    def __init__(self, proc: subprocess.Popen, on_exit: callable = None):
        self.proc = proc
        self.on_exit = on_exit

    @property
    def exited(self):
        proc = self.proc

        if proc.returncode is None:
            proc.poll()

        return proc.returncode is not None

    def kill(self):
        if not self.exited:
            os.kill(self.proc.pid, signal.SIGINT)

    def __del__(self):
        del self.proc


open_fds = []

processes: List[ProcessWrapper] = []
is_polling = False


@log_function
def _poll_processes() -> bool:
    """
    Makes sure zombie launchers are taken care of
    :return: Whether or not processes remain
    """
    global is_polling
    exited = []

    for proc in processes:
        if proc.exited:
            exited.append(proc)

            if proc.proc.returncode != 0:
                log.error(f"Process returned with non-zero exit code {proc.proc.returncode}")

    for proc in exited:
        processes.remove(proc)

        if callable(proc.on_exit):
            proc.on_exit()

        del proc

    processes_left = len(processes) > 0
    if not processes_left:
        is_polling = False
        log.info("No processes left to poll, exiting thread")

    return processes_left


def poll_processes():
    if is_polling:
        return

    log.info("Starting polling thread")

    from gi.repository import GObject
    GObject.timeout_add(100, _poll_processes)


def close_fds(*_, **__):
    log.info("Closing fds")

    for fd in open_fds:
        os.close(fd)

    open_fds.clear()

    from grapejuice_common.logs.log_vacuum import remove_empty_logs
    remove_empty_logs()


@log_function
def do_run_exe(
    command: List[str],
    exe_name: str,
    run_async: bool,
    env: Dict[str, str],
    working_directory: Optional[Path] = None,
    post_run_function: callable = None
) -> Union[ProcessWrapper, None]:
    log.info(f"Running exe {exe_name}")

    log_dir = paths.logging_directory()
    os.makedirs(log_dir, exist_ok=True)

    log.info("Opening log fds")

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    stdout_path = log_dir / f"{ts}_{exe_name}_stdout.log"
    stderr_path = log_dir / f"{ts}_{exe_name}_stderr.log"

    stdout_fd = os.open(stdout_path, os.O_WRONLY | os.O_CREAT)
    stderr_fd = os.open(stderr_path, os.O_WRONLY | os.O_CREAT)
    pty_fd, tty_fd = os.openpty()

    open_fds.extend((stdout_fd, stderr_fd, pty_fd, tty_fd))

    if run_async:
        log.info("Running process asynchronously")

        wrapper = ProcessWrapper(
            subprocess.Popen(
                command,
                env=env,
                stdin=tty_fd,
                stdout=stdout_fd,
                stderr=stderr_fd,
                cwd=working_directory
            ),
            on_exit=post_run_function
        )

        processes.append(wrapper)
        poll_processes()

        return wrapper

    else:
        log.info("Running process synchronously")

        subprocess.call(
            command,
            env=env,
            stdin=tty_fd,
            stdout=stdout_fd,
            stderr=stderr_fd,
            cwd=working_directory
        )

        if callable(post_run_function):
            post_run_function()

        return None


WINE_PROCESS_PTN = re.compile(r"^\s*([a-f0-9]+)\s+(\d+).*\'([\w.]+)\'")


@dataclass(frozen=True)
class WineProcess:
    pid: str
    threads: int
    image: str


DLL_OVERRIDE_SEP = ";"


def default_dll_overrides() -> List[str]:
    return [
        "dxdiagn=",  # Disable DX9 warning
        "winemenubuilder.exe="  # Prevent Roblox from making shortcuts
    ]


def _legacy_hardware_variables(configuration: WineprefixConfigurationModel):
    d = dict()
    if configuration.use_mesa_gl_override:
        d["MESA_GL_VERSION_OVERRIDE"] = "4.4"

    return d


def _validate_wine_home(home_path: Path):
    if not home_path.is_absolute():
        raise WineHomeInvalid(home_path, "The Wine home must be an absolute path which starts with '~' or '/'")

    if not home_path.exists():
        raise WineHomeInvalid(home_path, "The Wine home doesn't exist")

    if not home_path.is_dir():
        if home_path.name.startswith("wine") and home_path.parent.name == "bin":
            raise WineHomeInvalid(
                home_path,
                "The Wine home appears to be pointing at the Wine binary. However, the Wine home should be a "
                f"directory with 'bin/wine'. Consider changing the Wine home to '{home_path.parent.parent}'"
            )

        raise WineHomeInvalid(home_path, "The Wine home must be a directory")

    wine_bin = home_path / "bin"

    if not wine_bin.exists():
        raise WineHomeInvalid(home_path, f"The Wine home must contain a 'bin' directory at '{wine_bin}'")

    if not wine_bin.is_dir():
        raise WineHomeInvalid(home_path, f"'{wine_bin}' must be a directory")


class WineprefixCoreControl:
    _prefix_paths: WineprefixPaths
    _configuration: WineprefixConfigurationModel

    def __init__(self, prefix_paths: WineprefixPaths, configuration: WineprefixConfigurationModel):
        self._prefix_paths = prefix_paths
        self._configuration = configuration

    @property
    def wine_home(self) -> Path:
        from grapejuice_common import variables
        from grapejuice_common.features.settings import current_settings

        configured_homes = [
            self._configuration.wine_home.strip(),
            (current_settings.get_model().default_wine_home or "").strip()
        ]

        first_configured_home = next((x for x in configured_homes if x), None)

        def string_to_path(home_string: Union[Path, str]) -> Path:
            if isinstance(home_string, Path):
                return home_string

            if home_string.startswith(f"~{os.path.sep}"):
                return Path(home_string).expanduser()

            else:
                return Path(home_string)

        home_path = string_to_path(first_configured_home) if first_configured_home else variables.system_wine_home()

        try:
            _validate_wine_home(home_path)

        except WineHomeInvalid as e:
            log.error("Wine home is invalid")
            log.error(e)

            log.warning("Switching to system wine home")
            system_wine_home = variables.system_wine_home()
            if system_wine_home == home_path:
                log.error("System Wine Home was invalid?!")
                raise e

            home_path = system_wine_home

        log.info(f"Using Wine home '{home_path}'")

        return home_path

    @property
    def wine_bin(self):
        return self.wine_home / "bin"

    @property
    def dxvk_enabled(self) -> bool:
        return self._configuration.third_party.get(ThirdPartyKeys.dxvk, False)

    @property
    def dxvk_dll_overrides(self) -> List[str]:
        return list(map(lambda s: f"{s}=n", self._configuration.dxvk_overrides))

    def wine_binary(self, arch="") -> Path:
        log.info(f"Resolving wine binary for prefix {self._prefix_paths.base_directory}")

        wine_binary = self.wine_bin / f"wine{arch}"
        log.info(f"Resolved wine binary path: {wine_binary}")

        assert wine_binary.exists() and wine_binary.is_file(), f"Invalid wine binary: {wine_binary}"

        return wine_binary

    def wine_server(self) -> Path:
        path = self.wine_bin / "wineserver"
        assert path.exists(), f"Could not find wineserver at: {path}"

        return path

    def wine_dbg(self) -> Path:
        path = self.wine_bin / "winedbg"
        assert path.exists(), f"Could not find winedbg at: {path}"

        return path

    def _dri_prime_variables(self) -> Dict[str, str]:
        from grapejuice_common.features.settings import current_settings

        try:
            profile = current_settings.hardware_profile

        except HardwareProfilingError as e:
            log.error("Could not get hardware profile")
            log.error(e)

            return dict()

        prime_env = dict()

        if self._configuration.prime_offload_sink >= 0:
            sink = str(self._configuration.prime_offload_sink)

            prime_env = {"DRI_PRIME": sink}

            if profile.gpu_vendor is GPUVendor.NVIDIA:
                prime_env = {
                    **prime_env,
                    "__NV_PRIME_RENDER_OFFLOAD": sink,
                    "__VK_LAYER_NV_optimus": "NVIDIA_only",
                    "__GLX_VENDOR_LIBRARY_NAME": "nvidia"
                }

        log.info(f"PRIME environment variables: {json.dumps(prime_env)}")

        return prime_env

    def make_env(self, accelerate_graphics: bool = False) -> Dict[str, str]:
        user_env = self._configuration.env
        dll_overrides = list(filter(non_empty_string, self._configuration.dll_overrides.split(DLL_OVERRIDE_SEP)))
        dll_overrides.extend(default_dll_overrides())

        sanitize_environment = False
        # sanitize_environment = self._configuration.sanitize_environment
        # TODO: put behind feature flag

        if self.dxvk_enabled:
            dll_overrides.extend(self.dxvk_dll_overrides)

        # Inherit system environment
        if sanitize_environment:
            process_environment = {}

        else:
            process_environment = {**os.environ}

        process_environment = {
            **process_environment,
            "WINEDLLOVERRIDES": DLL_OVERRIDE_SEP.join(dll_overrides),
            **user_env,
            "WINEPREFIX": str(self._prefix_paths.base_directory),
            "WINEARCH": "win64",
            **(self._dri_prime_variables() if accelerate_graphics else dict()),
            **_legacy_hardware_variables(self._configuration)
        }

        # Variables in os.environ take priority
        for k, v in user_env.items():
            process_environment[k] = os.environ.get(k, v)

        # Wine generates giant logs for some people
        # Setting WINEDEBUG to -all *should* fix it
        if "WINEDEBUG" not in process_environment:
            winedebug_string = "-all"

            if self._configuration.enable_winedebug:
                winedebug_string = ""

                configuration_winedebug_string = self._configuration.winedebug_string.strip()
                if configuration_winedebug_string:
                    winedebug_string = configuration_winedebug_string

            process_environment["WINEDEBUG"] = winedebug_string

        # Make Wine defined in wine_home available in $PATH
        path_string = process_environment.get("PATH", None) or os.environ.get("PATH", None) or ""
        path_components = path_string.split(os.path.pathsep)
        wine_bin_string = str(self.wine_bin)

        if wine_bin_string not in path_components:
            path_components.insert(0, wine_bin_string)
            process_environment["PATH"] = os.path.pathsep.join(path_components)

        log.debug("Process environment: " + json.dumps(process_environment))

        if sanitize_environment:
            # Pass through user_passed_env
            env_passthrough = self._configuration.env_passthrough  # Reduce lookup time :)
            for k, v in os.environ.items():
                if k in env_passthrough:
                    process_environment[k] = v

        return process_environment

    def load_registry_file(
        self,
        registry_file: Path
    ):
        log.info(f"Loading registry file {registry_file} into the wineprefix")

        target_filename = str(int(time.time())) + ".reg"
        target_path = self._prefix_paths.temp_directory / target_filename
        target_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(registry_file, target_path)

        winreg = f"C:\\windows\\temp\\{target_filename}"
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=False)
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=True)

        os.remove(target_path)

    def load_patched_registry_files(
        self,
        registry_file: Path,
        patches: dict = None
    ):
        target_filename = str(int(time.time())) + ".reg"
        target_path = self._prefix_paths.temp_directory / target_filename

        with registry_file.open("r") as fp:
            template = Template(fp.read())

        with target_path.open("w+") as fp:
            fp.write(template.safe_substitute(patches))

        winreg = f"C:\\windows\\temp\\{target_filename}"
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=False)
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=True)

        os.remove(target_path)

    def block_microsoft_edge_webview2_installation(self):
        self._prefix_paths.program_files_x86_microsoft.mkdir(parents=True, mode=0x400, exist_ok=True)

    def unblock_microsoft_edge_webview2_installation(self):
        path = self._prefix_paths.program_files_x86_microsoft

        if path.exists():
            path.chmod(0o777)

    def disable_mime_associations(self):
        self.load_registry_file(paths.assets_directory() / "disable_mime_assoc.reg")

    def sandbox(self):
        user_dir = self._prefix_paths.user_directory

        if user_dir.exists() and user_dir.is_dir():
            for file in user_dir.glob("*"):
                if file.is_symlink():
                    log.info(f"Sandboxing {file}")
                    os.remove(file)
                    os.makedirs(file, exist_ok=True)

    def configure_prefix(self):
        self.disable_mime_associations()
        self.sandbox()

    def create_prefix(self):
        self.configure_prefix()

    def run_exe(
        self,
        exe_path: Union[Path, str],
        *args,
        run_async=False,
        use_wine64=False,
        accelerate_graphics: bool = False,
        post_run_function: callable = None,
        working_directory: Optional[Path] = None
    ) -> Union[ProcessWrapper, None]:
        log.info("Prepared environment for wine")

        if isinstance(exe_path, Path):
            exe_path_string = str(exe_path.resolve())
            exe_name = exe_path.name

            if not working_directory:
                working_directory = exe_path.parent

        elif isinstance(exe_path, str):
            exe_path_string = exe_path
            exe_name = exe_path.split(os.path.sep)[-1]

        else:
            raise ValueError(f"Invalid value type for exe_path: {type(exe_path)}")

        log.info(f"Resolved exe path to {exe_path_string}")

        env = self.make_env(accelerate_graphics)
        wine_binary = self.wine_binary("64" if use_wine64 else "")
        command = [str(wine_binary), exe_path_string, *args]

        return do_run_exe(
            command,
            exe_name,
            run_async,
            env,
            post_run_function=post_run_function,
            working_directory=working_directory
        )

    def run_linux_command(
        self,
        command: str,
        arguments: Optional[List[str]] = None,
        working_directory: Optional[Path] = None
    ):
        env = self.make_env()
        command_name = Path(command).name
        command = [command]

        if arguments:
            command.extend(arguments)

        return do_run_exe(
            command,
            command_name,
            run_async=False,
            env=env,
            working_directory=working_directory
        )

    def kill_wine_server(self):
        env = self.make_env()

        subprocess.check_call([str(self.wine_server()), "-k"], env=env)

    @property
    def process_list(self) -> List[WineProcess]:
        env = self.make_env()

        try:
            output = subprocess.check_output([str(self.wine_dbg()), "--command", "info proc"], env=env)
            output = output.decode("UTF-8")

        except subprocess.CalledProcessError as e:
            log.error(str(e))
            log.info("Could not get the process list through winedbg --command 'info proc'. Assume nothing is running")

            return []

        the_list = []
        for line in output.split("\n"):
            match = WINE_PROCESS_PTN.search(line.strip())

            if match:
                the_list.append(WineProcess(
                    match.group(1),
                    int(match.group(2)),
                    match.group(3)
                ))

        return the_list


atexit.register(close_fds)
