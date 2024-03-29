import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Generator, List, Iterable, Optional

from grapejuice_common import paths, variables
from grapejuice_common.errors import RobloxExecutableNotFound
from grapejuice_common.models.launch_uri import LaunchUri
from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.roblox_product import RobloxProduct, MAIN_ROBLOX_RELEASE_CHANNEL
from grapejuice_common.roblox_renderer import RobloxRenderer
from grapejuice_common.util import download_file, roblox_version
from grapejuice_common.util.enum_utils import enum_value_constrained_string
from grapejuice_common.wine.registry_file import RegistryFile
from grapejuice_common.wine.wineprefix_core_control import WineprefixCoreControl, ProcessWrapper
from grapejuice_common.wine.wineprefix_paths import WineprefixPaths

LOG = logging.getLogger(__name__)

ROBLOX_DOWNLOAD_URL = "https://www.roblox.com/download/client"


def _app_settings_path(executable_path: Path) -> Path:
    client_app_settings = executable_path.parent / "ClientSettings" / "ClientAppSettings.json"

    return client_app_settings


class WineprefixRoblox:
    _prefix_paths: WineprefixPaths
    _core_control: WineprefixCoreControl
    _configuration: WineprefixConfigurationModel

    def __init__(
        self,
        prefix_paths: WineprefixPaths,
        core_control: WineprefixCoreControl,
        configuration: WineprefixConfigurationModel
    ):
        self._prefix_paths = prefix_paths
        self._core_control = core_control
        self._configuration = configuration

    def download_installer(self):
        path = self.current_player_version_path / "RobloxPlayerLauncher.exe"

        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            LOG.debug(f"Removing old installer at {path}")
            os.remove(path)

        download_file(ROBLOX_DOWNLOAD_URL, path)

        if not self.is_installed:
            LOG.warning(f"Installer was downloaded to {path} but is_installed is false")

        return path

    def install_roblox(self, post_install_function: callable = None):
        self._core_control.create_prefix()
        self._core_control.block_microsoft_edge_webview2_installation()

        self._core_control.run_exe(
            self.download_installer(),
            post_run_function=post_install_function
        )

    def is_logged_into_studio(self) -> bool:
        with RegistryFile(self._prefix_paths.user_reg) as registry_file:
            registry_file.load()

            roblox_com = registry_file.find_key(r"Software\\Roblox\\RobloxStudioBrowser\\roblox.com")
            return (roblox_com is not None) and (roblox_com.get_attribute(".ROBLOSECURITY") is not None)

    def locate_all_roblox_executables_in_versions(self, executable_name: str) -> Generator[Path, None, None]:
        search_locations = [
            self._prefix_paths.roblox_appdata,
            self._prefix_paths.roblox_program_files
        ]

        for location in search_locations:
            versions_directory = location / "Versions"

            if location.exists() and versions_directory.exists() and versions_directory.is_dir():
                executable_path = versions_directory / executable_name

                if executable_path.exists() and executable_path.is_file():
                    yield executable_path

                for version in filter(Path.is_dir, versions_directory.glob("*")):
                    executable_path = version / executable_name

                    if executable_path.exists() and executable_path.is_file():
                        yield executable_path

    def locate_all_roblox_executables(self, executable_name: str) -> Generator[Path, None, None]:
        executable_path = self._prefix_paths.roblox_program_files / "Versions" / executable_name

        if executable_path.exists():
            yield executable_path

        for executable_path in self.locate_all_roblox_executables_in_versions(executable_name):
            yield executable_path

    def locate_roblox_executable(self, executable_name: str) -> Path:
        executable = next(self.locate_all_roblox_executables(executable_name), None)

        if executable is None:
            LOG.warning(f"Failed to locate Roblox executable: {executable_name}")
            raise RobloxExecutableNotFound(executable_name)

        return executable

    @property
    def roblox_studio_launcher_path(self) -> Path:
        return self.locate_roblox_executable("RobloxStudioLauncherBeta.exe")

    @property
    def roblox_studio_executable_path(self) -> Path:
        return self.locate_roblox_executable("RobloxStudioBeta.exe")

    @property
    def roblox_player_launcher_path(self) -> Path:
        return self.locate_roblox_executable("RobloxPlayerLauncher.exe")

    @property
    def fast_flag_dump_path(self) -> Path:
        def append_app_settings(p):
            return p / "ClientSettings" / "StudioAppSettings.json"

        possible_locations = list(map(append_app_settings, self._prefix_paths.possible_roblox_appdata))

        for location in possible_locations:
            if location.exists():
                return location

        return possible_locations[0]

    @property
    def versions_directory(self) -> Path:
        candidates = [
            *list(map(lambda p: p / "Versions", self._prefix_paths.possible_roblox_appdata)),
            self._prefix_paths.roblox_program_files / "Versions"
        ]

        pick = next(filter(lambda p: p.exists(), candidates), None)
        if not pick:
            # Pick program files as that's the directory chosen in non-staging
            pick = candidates[-1]

        return pick

    @property
    def current_player_version_path(self) -> Path:
        version = roblox_version.current_player_version(self._configuration.roblox_release_channel)
        return self.versions_directory / version

    @property
    def current_studio_version_path(self) -> Path:
        version = roblox_version.current_studio_version(self._configuration.roblox_release_channel)
        return self.versions_directory / version

    @property
    def current_player_version_settings_path(self):
        return _app_settings_path(self.current_player_version_path / "RobloxPlayerBeta.exe")

    @property
    def current_studio_version_settings_path(self):
        return _app_settings_path(self.current_studio_version_path / "RobloxPlayerBeta.exe")

    @property
    def roblox_studio_app_settings_path(self) -> Path:
        return _app_settings_path(self.roblox_studio_executable_path)

    @property
    def roblox_player_app_settings_path(self) -> Path:
        return _app_settings_path(self.roblox_player_launcher_path)

    @property
    def all_studio_app_settings_paths(self) -> List[Path]:
        ls = list(map(_app_settings_path, self.locate_all_roblox_executables("RobloxStudioBeta.exe")))
        ls.append(self.current_studio_version_settings_path)

        return list(set(ls))

    @property
    def all_player_app_settings_paths(self) -> List[Path]:
        ls = list(map(_app_settings_path, self.locate_all_roblox_executables("RobloxPlayerLauncher.exe")))
        ls.append(self.current_player_version_settings_path)

        return list(set(ls))

    @property
    def is_installed(self) -> bool:
        try:
            self.locate_roblox_executable("RobloxPlayerLauncher.exe")
            return True

        except RobloxExecutableNotFound:
            return False

    def _rewrite_uri(self, uri: Optional[str] = None) -> Optional[str]:
        """
        Add custom launch options to the URI provided by roblox
        :param uri: The roblox uri to be parsed
        :return: (Maybe) edited roblox uri
        """
        if uri is None:
            return None

        parsed_uri = LaunchUri(uri)

        if self._configuration.roblox_release_channel != MAIN_ROBLOX_RELEASE_CHANNEL:
            LOG.info(
                f"Updating roblox launch URI to use release channel {self._configuration.roblox_release_channel.value}")
            parsed_uri.channel = self._configuration.roblox_release_channel

        return parsed_uri.as_string

    def _write_flags(self, product: RobloxProduct, settings_paths: Iterable[Path]):
        flags = self._configuration.fast_flags.get(enum_value_constrained_string(product), None) or dict()

        # Apply rendering flag
        renderer = RobloxRenderer(self._configuration.roblox_renderer)
        if renderer is not RobloxRenderer.Undetermined:
            flags[renderer.prefer_flag] = True

        # Apply target fps flag
        if self._configuration.roblox_set_target_fps:
            flags["DFIntTaskSchedulerTargetFps"] = int(self._configuration.roblox_scheduler_target_fps)

        # Don't do anything when we don't have any flags
        if len(flags) <= 0:
            return

        json_dump = json.dumps(flags, indent=2)

        for p in settings_paths:
            LOG.info(f"Writing flags for {product} to: {p}")
            p.parent.mkdir(parents=True, exist_ok=True)

            with p.open("w+", encoding=variables.text_encoding()) as fp:
                fp.write(json_dump)

    def run_roblox_studio(self, uri: str = None, ide: bool = False):
        launcher_path = self.roblox_studio_launcher_path
        uri = self._rewrite_uri(uri)

        self._write_flags(RobloxProduct.studio, self.all_studio_app_settings_paths)

        launch_args = [launcher_path]
        launch_args.extend(list(
            filter(
                None,
                [
                    "-ide" if ide else None,
                    uri
                ]
            )
        ))

        self._core_control.run_exe(*launch_args, accelerate_graphics=True)

    def run_roblox_player(self, uri):
        player_launcher_path = self.roblox_player_launcher_path
        uri = self._rewrite_uri(uri)

        product = RobloxProduct.app if uri == variables.roblox_app_experience_url() else RobloxProduct.player
        self._write_flags(product, self.all_player_app_settings_paths)

        self._core_control.run_exe(player_launcher_path, uri, accelerate_graphics=True)

    def launch_app(self):
        player_executable_path = self.locate_roblox_executable("RobloxPlayerLauncher.exe")

        product = RobloxProduct.app
        self._write_flags(product, self.all_player_app_settings_paths)

        launch_args = ["-app"]
        if self._configuration.roblox_release_channel != MAIN_ROBLOX_RELEASE_CHANNEL:
            launch_args = ["-channel", self._configuration.roblox_release_channel.value, *launch_args]

        self._core_control.run_exe(player_executable_path, *launch_args, accelerate_graphics=True)

    def run_roblox_studio_with_events(self, run_async: bool = True, **events) -> ProcessWrapper:
        roblox_studio_path = self.roblox_studio_executable_path

        launch_args = [roblox_studio_path]

        for k, v in events.items():
            launch_args.append("-" + k)
            launch_args.append(v)

        if self._configuration.roblox_release_channel != MAIN_ROBLOX_RELEASE_CHANNEL:
            launch_args = ["-channel", self._configuration.roblox_release_channel.value, *launch_args]

        return self._core_control.run_exe(*launch_args, run_async=run_async)

    def extract_fast_flags(self):
        fast_flag_path = self.fast_flag_dump_path

        if fast_flag_path.exists():
            os.remove(fast_flag_path)

        studio_process = self.run_roblox_studio_with_events(startEvent="FFlagExtract", showEvent="NoSplashScreen")

        def fast_flags_present():
            if fast_flag_path.exists():
                stat = os.stat(fast_flag_path)

                if stat.st_size > 0:
                    return True

            return False

        while not fast_flags_present():
            time.sleep(0.1)

        shutil.copy(fast_flag_path, paths.fast_flag_cache_location())

        if studio_process:
            studio_process.kill()
            time.sleep(1)  # Give Roblox a chance
            self._core_control.kill_wine_server()

    def authenticate_studio(self, ticket: str):
        self._write_flags(RobloxProduct.studio, self.all_studio_app_settings_paths)

        run_args = [self.roblox_studio_executable_path, ticket]

        self._core_control.run_exe(*run_args, accelerate_graphics=True)
