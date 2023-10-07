from typing import Optional, List, Dict, Any

from grapejuice_common.hardware_info.hardware_profile import HardwareProfile
from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.util.pydantic_loader import pydantic_v1

current_version: int = 4


class SettingsModel(pydantic_v1.BaseModel):
    version: int = current_version
    hardware_profile: Optional[HardwareProfile] = None

    show_fast_flag_warning: bool = True
    release_channel: str = "master"
    disable_updates: bool = False
    try_profiling_hardware: bool = True
    default_wine_home: Optional[str] = ""
    wineprefixes: List[WineprefixConfigurationModel] = []
    unsupported_settings: Dict[str, Any] = {}
    performed_first_time_setup = False

    def update_version(self) -> bool:
        did_update = self.version != current_version
        self.version = current_version

        return did_update
