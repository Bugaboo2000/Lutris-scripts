import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from gettext import gettext as _
from pathlib import Path
from typing import Optional

from grapejuice import background
from grapejuice_common import paths
from grapejuice_common.recipes.delete_edge_update_service_recipe import DeleteEdgeUpdateServiceRecipe
from grapejuice_common.recipes.dxvk_recipes import InstallDXVKRecipe, UninstallDXVKRecipe
from grapejuice_common.recipes.install_microsoft_edge_webview_2 import InstallMicrosoftEdgeWebview2Recipe
from grapejuice_common.recipes.restore_edge_update_service_recipe import RestoreEdgeUpdateServiceRecipe
from grapejuice_common.update_info_providers import UpdateInformationProvider
from grapejuice_common.util import xdg_open
from grapejuice_common.wine.wineprefix import Wineprefix


class RunRobloxStudio(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(_("Launching Roblox Studio"), **kwargs)

        self._prefix = prefix

    def work(self) -> None:
        from grapejuice_common.abstraction.abstracted_instance import abstract_grapejuice
        abstract_grapejuice().launch_studio(self._prefix.configuration.id)


class OpenRobloxApp(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(_("Launching Roblox App"), **kwargs)

        self._prefix = prefix

    def work(self) -> None:
        from grapejuice_common.abstraction.abstracted_instance import abstract_grapejuice
        abstract_grapejuice().launch_app(self._prefix.configuration.id)


class ExtractFastFlags(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(_("Extracting Fast Flags"), **kwargs)

        self._prefix = prefix

    def work(self) -> None:
        from grapejuice_common.abstraction.abstracted_instance import abstract_grapejuice

        should_extract_flags = True

        # Only check fast flags every x minutes, checking more often is overkill
        # This also reduces overall compute time used, yay!

        if paths.fast_flag_cache_location().exists():
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)

            stat = os.stat(paths.fast_flag_cache_location())
            if stat.st_mtime > ten_minutes_ago.timestamp():
                should_extract_flags = False

        if should_extract_flags:
            abstract_grapejuice().extract_fast_flags()

        else:
            time.sleep(1)  # Make it feel like Grapejuice is doing something


class OpenLogsDirectory(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__(_("Opening logs directory"), **kwargs)

    def work(self) -> None:
        path = paths.logging_directory()
        path.mkdir(parents=True, exist_ok=True)

        xdg_open(path)


class OpenConfigFile(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__(_("Opening configuration file"), **kwargs)

    def work(self) -> None:
        xdg_open(paths.grapejuice_user_settings())


class PerformUpdate(background.BackgroundTask):
    def __init__(self, update_provider: UpdateInformationProvider, reopen: bool = False, **kwargs):
        super().__init__(name=_("Performing update"), **kwargs)
        self._update_provider = update_provider
        self._reopen = reopen

    def work(self) -> None:
        self._update_provider.do_update()

        if self._reopen:
            subprocess.Popen(["bash", "-c", f"{sys.executable} -m grapejuice gui & disown"], preexec_fn=os.setpgrp)

            from gi.repository import Gtk
            Gtk.main_quit()

            sys.exit(0)


class InstallRoblox(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(_("Installing Roblox in {prefix}").format(prefix=prefix.configuration.display_name), **kwargs)
        self._prefix = prefix

    def work(self):
        def update_edge_state():
            if self._prefix.configuration.disable_edge_update:
                recipe = DeleteEdgeUpdateServiceRecipe()

            else:
                recipe = RestoreEdgeUpdateServiceRecipe()

            if not recipe.exists_in(self._prefix):
                recipe.make_in(self._prefix)

        self._prefix.roblox.install_roblox(post_install_function=update_edge_state)


class ShowDriveC(background.BackgroundTask):
    _path: Path

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(_("Opening Drive C in {prefix}").format(prefix=prefix.configuration.display_name), **kwargs)
        self._path = prefix.paths.drive_c

    def work(self):
        xdg_open(str(self._path))


class SignIntoStudio(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__(_("Opening Studio's sign-in page"), **kwargs)

    def work(self):
        from grapejuice_common import variables
        xdg_open(variables.roblox_return_to_studio())


class FaultyOnPurpose(background.BackgroundTask):
    _timeout: int

    def __init__(self, timeout: Optional[int] = None, **kwargs):
        super().__init__("Causing problems", **kwargs)
        self._timeout = timeout or random.randint(2, 5)

    def work(self):
        try:
            time.sleep(self._timeout)

        except KeyboardInterrupt:
            pass

        raise RuntimeError("Woops 😈")


class RunBuiltinWineApp(background.BackgroundTask):
    _prefix: Wineprefix
    _app: str

    def __init__(self, prefix: Wineprefix, app: str, **kwargs):
        super().__init__(
            _("Running {app} in {prefix}").format(app=app, prefix=prefix.configuration.display_name),
            **kwargs
        )

        self._prefix = prefix
        self._app = app

    def work(self):
        self._prefix.core_control.run_exe(self._app)


class RunLinuxApp(background.BackgroundTask):
    _prefix: Wineprefix
    _app: str

    def __init__(self, prefix: Wineprefix, app: str, **kwargs):
        super().__init__(
            _("Running {app} in {prefix}").format(app=app, prefix=prefix.configuration.display_name),
            **kwargs
        )

        self._prefix = prefix
        self._app = app

    def work(self):
        self._prefix.core_control.run_linux_command(self._app)


class KillWineserver(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(
            _("Killing wineserver for {prefix}").format(prefix=prefix.configuration.display_name),
            **kwargs
        )

        self._prefix = prefix

    def work(self):
        try:
            self._prefix.core_control.kill_wine_server()

        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                self._log.warning(str(e))
                self._log.info(
                    "There was an error trying to kill the Wine server, "
                    "sunk the error assuming there wasn't one"
                )

            else:
                raise e


class SetDXVKState(background.BackgroundTask):
    _prefix: Wineprefix
    _should_be_installed: bool

    def __init__(self, prefix: Wineprefix, should_be_installed: bool, **kwargs):
        super().__init__(
            _("Updating DXVK state for {prefix}").format(prefix=prefix.configuration.display_name),
            **kwargs
        )

        self._prefix = prefix
        self._should_be_installed = should_be_installed

    def work(self):
        recipe = InstallDXVKRecipe() if self._should_be_installed else UninstallDXVKRecipe()

        if not recipe.exists_in(self._prefix):
            recipe.make_in(self._prefix)


class PreloadXRandR(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__(_("Preloading XRandR interface"), **kwargs)

    def work(self):
        from grapejuice_common.hardware_info.xrandr_factory import xrandr_factory
        x = xrandr_factory()

        self._log.info(f"Have {len(x.providers)} providers on a {type(x)} instance!")


class InstallMicrosoftEdgeWebview2(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__("Installing MS Edge Webview2", **kwargs)
        self._prefix = prefix

    def work(self):
        recipe = InstallMicrosoftEdgeWebview2Recipe()
        if not recipe.exists_in(self._prefix):
            recipe.make_in(self._prefix)
