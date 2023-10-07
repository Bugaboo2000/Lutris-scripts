import json
import logging
from pathlib import Path
from typing import Dict, Optional, Callable, TypeVar, Any

from grapejuice_common import paths, variables
from grapejuice_common.errors import HardwareProfilingError, NoHardwareProfile, PresentableError
from grapejuice_common.hardware_info import hardware_profile
from grapejuice_common.hardware_info.hardware_profile import HardwareProfile, profile_hardware
from grapejuice_common.models.settings_model import SettingsModel
from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.util.pydantic_loader import pydantic_v1

LOG = logging.getLogger(__name__)


def current_settings_version() -> int:
    return SettingsModel().version


AccessedType = TypeVar("AccessedType")


def default_settings() -> SettingsModel:
    return SettingsModel()


def _text_encoding():
    from grapejuice_common.variables import text_encoding
    return text_encoding()


def _remove_legacy_dunder_fields_from_settings_object(so: Dict[str, Any]) -> bool:
    """
    Removes and key from the Dict that starts and ends with __. For example: __version__.
    They are renamed to the dunderless variant: __version__ -> version
    The operation is in-place, so this function returns a success boolean

    Old versions of Grapejuice had these keys in the settings file, which was a silly choice because a dunder variable
    is reserved for Python internal code. This caused conflicts when migrating to Pydantic. Pydantic no longer
    supports auto-renaming this, so we have to do it ourselves now.
    :param so: Raw Settings Object
    :return: Boolean that indicates that keys have been modified
    """
    dunder_keys = [k for k in so.keys() if k.startswith("__") and k.endswith("__")]
    replacements = [k.strip("_") for k in dunder_keys]

    for old_key, new_key in zip(dunder_keys, replacements):
        so[new_key] = so[old_key]
        so.pop(old_key)

    return len(replacements) > 0


class SettingsManager:
    _settings_model: SettingsModel = None
    _location: Path = None

    def __init__(self, file_location=paths.grapejuice_user_settings()):
        self._location = file_location
        self.load()

    def perform_migrations(self, desired_migration_version: int = current_settings_version()):
        if self.version == desired_migration_version:
            LOG.debug(f"Settings file is up to date at version {self.version}")
            return

        a = self.version
        LOG.info(f"Performing migration from {a} to {desired_migration_version}")

        direction = 1 if desired_migration_version > a else -1

        def set_model_version(mdl: SettingsModel, version: int):
            mdl.version = version

        for x in range(a + direction, desired_migration_version + direction, direction):
            index = (a, x)
            LOG.info(f"Migration index {index}")
            from grapejuice_common.features.settings_migration import migration_index

            migration_function = migration_index.get(index, None)

            if callable(migration_function):
                LOG.info(f"Applying migration {index}: {migration_function}")
                new_model = migration_function(self._settings_model)

                if new_model is not None:
                    self._settings_model = new_model

                LOG.info(f"Applying and saving new settings version {x}")

                self.update_model(set_model_version, x)

            else:
                LOG.warning(f"Migration {index} is invalid")

            a = x

    @property
    def version(self) -> int:
        return self._settings_model.version

    @property
    def hardware_profile(self) -> HardwareProfile:
        if self._profile_hardware():
            self.save()

        profile = self._settings_model.hardware_profile
        if profile is None:
            raise NoHardwareProfile()

        return profile

    def _sort_wineprefixes(self):
        self._settings_model.wineprefixes = list(sorted(
            self._settings_model.wineprefixes,
            key=lambda wp: 999 if wp.priority is None else wp.priority
        ))

    def find_wineprefix(self, search_id: str) -> Optional[WineprefixConfigurationModel]:
        def match_prefix(pfx: WineprefixConfigurationModel) -> bool:
            return pfx.id == search_id

        candidates = list(filter(match_prefix, self._settings_model.wineprefixes))
        if len(candidates) > 0:
            return candidates[0]

        return None

    def _profile_hardware(self, always_profile: Optional[bool] = False) -> bool:
        """
        Profile the hardware of the machine Grapejuice is running on. This method may silently
        fail as profiling hardware is quite a complex task. Due to this, the return value
        of this method is a boolean indicating if the caller should save the Grapejuice settings.
        :param always_profile: Override any logic in the method, and just go ahead with the profiling
        :return: Boolean indicating whether settings should be saved or not.
        """
        saved_profile: Optional[HardwareProfile] = None if always_profile else self._settings_model.hardware_profile

        if not self._settings_model.try_profiling_hardware:
            return False

        if saved_profile:
            from grapejuice_common.hardware_info.lspci import LSPci

            try:
                hardware_list = LSPci()

            except Exception as e:
                LOG.info("Failed to get LSPci info: " + str(e))

                return False

            should_profile_hardware = (hardware_list.graphics_id != saved_profile.graphics_id) or \
                                      (saved_profile.version != hardware_profile.current_version)

        else:
            should_profile_hardware = True

        if should_profile_hardware:
            LOG.info("Going to profile hardware")

            try:
                self._settings_model.hardware_profile = profile_hardware()

            except HardwareProfilingError as e:
                LOG.error("Failed to profile hardware: " + str(e))
                LOG.info("No longer try to profile hardware due to errors")

                def set_try_profiling_hardware(mdl: SettingsModel, x: bool):
                    mdl.try_profiling_hardware = x

                self.update_model(set_try_profiling_hardware, False)

            return True

        return False

    def load(self):
        save_settings = False

        def raise_presentable_loading_error(ex):
            raise PresentableError(
                title="Invalid settings file",
                description="Grapejuice could not properly decode the information in the user settings file. This "
                            "is most likely due to a formatting error in the actual settings file. Did you make a "
                            "mistake while manually editing the file?",
                cause=ex
            )

        if self._location.exists():
            LOG.debug(f"Loading settings from '{self._location}'")

            try:
                with self._location.open("r", encoding=variables.text_encoding()) as fp:
                    settings_string = fp.read()

                if settings_string.strip():
                    raw_settings_object = json.loads(settings_string)

                    removed_dunder_keys = _remove_legacy_dunder_fields_from_settings_object(raw_settings_object)
                    self._settings_model = SettingsModel.parse_obj(raw_settings_object)

                    save_settings = save_settings or removed_dunder_keys or self._settings_model.update_version()

                else:
                    LOG.warning("Found empty settings file! Using default settings")
                    self._settings_model = default_settings()
                    save_settings = True

            except json.JSONDecodeError as e:
                raise_presentable_loading_error(e)

            except pydantic_v1.ValidationError as e:
                raise_presentable_loading_error(e)

        else:
            LOG.info("There is no settings file present, going to save one")
            self._settings_model = default_settings()
            save_settings = True

        save_settings = self._profile_hardware() or save_settings

        if save_settings:
            LOG.info("Saving settings after load, because something was wrong or needs updating")
            self.save()

    def save(self):
        LOG.debug(f"Saving settings file to '{self._location}'")

        # Sort wineprefixes before saving so the file order matches the UI
        self._sort_wineprefixes()
        self._settings_model.update_version()

        # Perform actual save
        self._location.parent.mkdir(parents=True, exist_ok=True)
        with self._location.open("w+", encoding=_text_encoding()) as fp:
            json_string = self._settings_model.json(indent=2)
            fp.write(json_string)

    def update_model(self, update_fn: Callable[[SettingsModel, Optional[Any]], None], *args, **kwargs):
        update_fn(self._settings_model, *args, **kwargs)
        self.save()

    def _access_model(self, access_fn: Callable[[SettingsModel], AccessedType]) -> AccessedType:
        return access_fn(self._settings_model)

    def get_model(self) -> SettingsModel:
        return self._settings_model.copy()

    def save_prefix_model(self, model: WineprefixConfigurationModel):
        def is_not_input_model(pfx: WineprefixConfigurationModel) -> bool:
            return pfx.id != model.id

        self._settings_model.wineprefixes = [
            *list(filter(is_not_input_model, self._settings_model.wineprefixes)),
            model
        ]

        self.save()

    def remove_prefix_model(self, model: WineprefixConfigurationModel):
        def is_not_input_model(pfx: WineprefixConfigurationModel):
            return pfx.id != model.id

        self._settings_model.wineprefixes = list(
            filter(
                is_not_input_model,
                self._settings_model.wineprefixes
            )
        )

        self.save()

    def as_dict(self) -> Dict:
        return self._settings_model.dict()

    def apply_dict(self, d: Dict):
        self._settings_model = SettingsModel.parse_obj({
            **self._settings_model.dict(),
            **d
        })


current_settings = SettingsManager()
