import re
from pathlib import Path
from typing import Dict, List, Any

from grapejuice_common.models.fast_flags import FastFlagValueType
from grapejuice_common.roblox_product import RobloxReleaseChannel
from grapejuice_common.roblox_renderer import RobloxRenderer
from grapejuice_common.util.pydantic_loader import pydantic_v1
from grapejuice_common.wine.wineprefix_hints import WineprefixHint


class ThirdPartyKeys:
    dxvk = "dxvk"


DEFAULT_ENV_PASSTHROUGH = [
    "HOME",  # Required for MangoHud to function
    "DISPLAY",  # Xorg Display, required for Xorg to work
    "XAUTHORITY",  # Xorg session cookie, required for XWayland
    "WAYLAND_DISPLAY",  # Wayland display, required for Wayland to work
    "LANG",  # Localization
    "TZ",  # Timezone
    "XDG_RUNTIME_DIR",  # Points to /run/user/$UID. Required for Wine FS
    "XDG_SESSION_TYPE",  # Communicates display protocol being used
    "XDG_CONFIG_HOME",  # Required for MangoHud to function
    "XDG_DATA_HOME",  # Required for MangoHud to function
    "LD_LIBRARY_PATH",  # Additional system libraries
    "LD_PRELOAD",  # Preloaded libraries, often used for hotfixes
    "MANGOHUD"  # Commonly used performance monitoring app
]


class WineprefixConfigurationModel(pydantic_v1.BaseModel):
    id: str
    priority: int
    name_on_disk: str
    display_name: str
    wine_home: str
    dll_overrides: str
    disable_edge_update: bool = True
    prime_offload_sink: int = -1
    use_mesa_gl_override: bool = False
    enable_winedebug: bool = False
    winedebug_string: str = ""
    roblox_release_channel: RobloxReleaseChannel = RobloxReleaseChannel.LIVE
    roblox_renderer: str = RobloxRenderer.Undetermined.value
    roblox_set_target_fps: bool = False
    roblox_scheduler_target_fps: int = 144
    env: Dict[str, str] = {}
    sanitize_environment: bool = False
    env_passthrough: List[str] = DEFAULT_ENV_PASSTHROUGH
    hints: List[str] = []
    fast_flags: Dict[str, Dict[str, FastFlagValueType]] = {}
    third_party: Dict[str, bool] = {}
    dxvk_overrides: List[str] = ["d3d11", "d3d9", "dxgi", "d3d10core"]

    @property
    def hints_as_enum(self) -> List[WineprefixHint]:
        return list(map(WineprefixHint, self.hints))

    @property
    def base_directory(self) -> Path:
        from grapejuice_common import paths

        return paths.wineprefixes_directory() / self.name_on_disk

    @property
    def exists_on_disk(self):
        return self.base_directory.exists()

    def create_name_on_disk_from_display_name(self):
        from unidecode import unidecode

        s = unidecode(self.display_name)  # Remove wacky non-ascii characters
        s = s.strip()  # Remove surrounding whitespace
        s = re.sub(r"\s+/\s+", "_", s)  # Replace slashes surrounded by whitespace by a single underscore
        s = re.sub(r"[/ \W]+", "_", s)
        s = s.lower()

        self.name_on_disk = s

    def apply_dict(self, d: Dict[str, Any]):
        for k, v in d.items():
            setattr(self, k, v)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)
