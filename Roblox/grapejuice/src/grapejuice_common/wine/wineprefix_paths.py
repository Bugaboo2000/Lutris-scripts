import getpass
from pathlib import Path
from typing import List


class WineprefixPaths:
    _base_directory: Path

    def __init__(self, base_directory: Path):
        self._base_directory = base_directory

    @property
    def base_directory(self) -> Path:
        return self._base_directory

    @property
    def present_on_disk(self) -> bool:
        return self._base_directory.exists()

    @property
    def drive_c(self) -> Path:
        return self._base_directory / "drive_c"

    @property
    def user_reg(self) -> Path:
        return self._base_directory / "user.reg"

    @property
    def roblox_program_files(self) -> Path:
        return self.drive_c / "Program Files (x86)" / "Roblox"

    @property
    def program_files_x86_microsoft(self) -> Path:
        return self.drive_c / "Program Files (x86)" / "Microsoft"

    @property
    def local_appdata(self):
        return self.user_directory / "Local" / "AppData"

    @property
    def temp_directory(self):
        return self.drive_c / "windows" / "temp"

    @property
    def user_directory(self):
        return self.drive_c / "users" / getpass.getuser()

    @property
    def possible_roblox_appdata(self) -> List[Path]:
        return [
            self.user_directory / "AppData" / "Local" / "Roblox",
            self.user_directory / "Local Settings" / "Application Data" / "Roblox"
        ]

    @property
    def roblox_appdata(self):
        possible_locations = self.possible_roblox_appdata

        for location in possible_locations:
            if location.exists():
                return location

        return possible_locations[0]

    @property
    def grapejuice_in_drive_c(self):
        return self.drive_c / "Grapejuice"

    @property
    def vendor_directory(self):
        return self.grapejuice_in_drive_c / "Vendor"

    @property
    def system_registry_hive(self):
        return self._base_directory / "system.reg"

    @property
    def user_registry_hive(self):
        return self._base_directory / "user.reg"

    @property
    def dxvk_directory(self):
        return self.vendor_directory / "DXVK"

    @property
    def edge_webview_directory(self):
        return self.vendor_directory / "microsoft-edge-webview2"

    @property
    def windows(self) -> Path:
        for p in self.drive_c.glob("*"):
            if p.name.lower() == "windows" and p.is_dir():
                return p

        raise RuntimeError(f"Could not find windows directory in {self.drive_c}")

    @property
    def system32(self) -> Path:
        for p in self.windows.glob("*"):
            if p.name.lower() == "system32" and p.is_dir():
                return p

        raise RuntimeError(f"Could not find System32 directory in {self.drive_c}")

    @property
    def syswow64(self) -> Path:
        for p in self.windows.glob("*"):
            if p.name.lower() == "syswow64" and p.is_dir():
                return p

        raise RuntimeError(f"Could not find SysWOW64 directory in {self.drive_c}")
