import json
import logging
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Dict

from grapejuice_common import paths
from grapejuice_common.errors import RobloxExecutableNotFound
from grapejuice_common.models.fast_flags import FastFlagDictionary
from grapejuice_common.models.settings_model import SettingsModel
from grapejuice_common.models.wineprefix_configuration_model import ThirdPartyKeys
from grapejuice_common.roblox_product import RobloxProduct
from grapejuice_common.util.enum_utils import enum_value_constrained_string
from grapejuice_common.wine.wineprefix import Wineprefix

migration_index = dict()

log = logging.getLogger(__name__)

# Legacy setting keys
k_version = "__version__"  # Magic variable gets underscores
k_hardware_profile = "__hardware_profile__"

k_show_fast_flag_warning = "show_fast_flag_warning"
k_wine_binary = "wine_binary"
k_dll_overrides = "dll_overrides"
k_release_channel = "release_channel"
k_environment_variables = "env"
k_disable_updates = "disable_updates"
k_wineprefixes = "wineprefixes"
k_enabled_tweaks = "enabled_tweaks"
k_unsupported_settings = "unsupported_settings"
k_try_profiling_hardware = "try_profiling_hardware"


def register_migration(version_from: int, version_to: int):
    def decorator(migration_function):
        migration_index[(version_from, version_to)] = migration_function

        return migration_function

    return decorator


# Keep migrations between 0 and 1 even though they don't do anything
# Having these run is an indicator that the feature is working

@register_migration(0, 1)
def migration_one(_settings: Dict):
    log.info("Migration one application")


@register_migration(1, 0)
def undo_migration_one(_settings: Dict):
    log.info("Migration one undo")


def _get_wine_home(wine_binary_string: str, default_value: str) -> str:
    if not wine_binary_string:
        return default_value

    wine_binary = Path(wine_binary_string)
    can_be_used = False

    if wine_binary.name != "wine":
        log.warning("Could not migrate Wine binary because its name is not 'wine'")

    elif wine_binary.parent.name != "bin":
        log.warning("Could not migrate Wine binary because it's not in a folder named 'bin'")

    else:
        can_be_used = True

    return str(wine_binary.parent.parent) if can_be_used else default_value


def _get_fast_flags(prefix: Wineprefix) -> Dict[str, FastFlagDictionary]:
    studio_fast_flags: FastFlagDictionary = {}
    player_fast_flags: FastFlagDictionary = {}

    try:
        with prefix.roblox.roblox_studio_app_settings_path.open("r") as fp:
            studio_fast_flags = json.load(fp)

    except (FileNotFoundError, RobloxExecutableNotFound):
        pass

    try:
        with prefix.roblox.roblox_player_app_settings_path.open("r") as fp:
            player_fast_flags = json.load(fp)

    except (FileNotFoundError, RobloxExecutableNotFound):
        pass

    return {
        enum_value_constrained_string(RobloxProduct.studio): studio_fast_flags,
        enum_value_constrained_string(RobloxProduct.player): player_fast_flags,
        enum_value_constrained_string(RobloxProduct.player): player_fast_flags
    }


@register_migration(1, 2)
def upgrade_wineprefix(settings_object: Dict):
    from grapejuice_common.features.wineprefix_migration import do_wineprefix_migration
    from grapejuice_common.wine.wine_functions import create_player_prefix_model, create_studio_prefix_model

    prefixes = settings_object.get(k_wineprefixes, [])

    if len(prefixes) > 0:
        return

    new_player_prefix = create_player_prefix_model(settings_object)
    new_studio_prefix = create_studio_prefix_model(settings_object)
    unsupported_settings = settings_object.get("unsupported_settings", {})

    legacy_wineprefix_path = paths.local_share_grapejuice() / "wineprefix"
    do_wineprefix_migration(
        legacy_wineprefix_path=legacy_wineprefix_path,
        new_name_on_disk=new_player_prefix.name_on_disk
    )
    do_wineprefix_migration(
        legacy_wineprefix_path=legacy_wineprefix_path,
        new_name_on_disk=new_studio_prefix.name_on_disk
    )

    for prefix_configuration in (new_player_prefix, new_studio_prefix):
        prefix = Wineprefix(prefix_configuration)

        prefix_configuration.wine_home = _get_wine_home(
            unsupported_settings.get(k_wine_binary, ""),
            prefix_configuration.wine_home
        )

        if k_dll_overrides in unsupported_settings:
            prefix_configuration.dll_overrides = unsupported_settings.get(k_dll_overrides)

        prefix_configuration.fast_flags = _get_fast_flags(prefix)

        env = dict(unsupported_settings.get(k_environment_variables, {}))
        if env.get("MESA_GL_VERSION_OVERRIDE", "") == "4.4":
            prefix_configuration.use_mesa_gl_override = True
            env.pop("MESA_GL_VERSION_OVERRIDE")

        if "WINEDEBUG" in env:
            prefix_configuration.enable_winedebug = True
            prefix_configuration.winedebug_string = env.pop("WINEDEBUG")

        prefix_configuration.env = env

        prefix_configuration.third_party = {
            ThirdPartyKeys.dxvk: False
        }

    prefixes.extend(list(map(asdict, [new_player_prefix, new_studio_prefix])))

    settings_object[k_wineprefixes] = prefixes


@register_migration(2, 1)
def downgrade_wineprefix(settings_object: Dict):
    if len(settings_object[k_wineprefixes]) <= 0:
        return

    settings_object["env"] = settings_object[k_wineprefixes][0].get("env", dict())

    original_prefix_path = paths.local_share_grapejuice() / "wineprefix"
    new_prefix_path = paths.wineprefixes_directory() / settings_object[k_wineprefixes][0]["name_on_disk"]

    # Try to not destroy any prefixes
    if original_prefix_path.exists():
        if original_prefix_path.is_symlink():
            os.remove(original_prefix_path)

        else:
            n = 1
            while original_prefix_path.exists():
                original_prefix_path = paths.local_share_grapejuice() / f"wineprefix ({n})"
                n += 1

    original_prefix_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(new_prefix_path, original_prefix_path)


@register_migration(2, 3)
def use_pydantic(_user_settings: Dict):
    # Pydantic handles this one
    ...


@register_migration(3, 2)
def stop_using_pydantic(_settings_model: SettingsModel):
    settings_object = _settings_model.dict()
    settings_object["__version__"] = settings_object.pop("version", 2)
    settings_object["__hardware_profile__"] = settings_object.pop("hardware_profile", None)
