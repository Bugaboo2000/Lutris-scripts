import logging
from typing import Dict, Any, Optional

from grapejuice_common.roblox_product import RobloxReleaseChannel, MAIN_ROBLOX_RELEASE_CHANNEL

log = logging.getLogger(__name__)


def _split_uri_part(part):
    spl = part.split(":", maxsplit=1)

    if len(spl) == 1:
        spl.append("")

    return spl


class LaunchUri:
    _initial_uri: str
    _as_dict: Dict[str, Any]

    def __init__(self, uri: str):
        self._initial_uri = uri

        if uri.strip():
            self._as_dict = dict([_split_uri_part(x) for x in uri.split("+")])

        else:
            self._as_dict = {}

    def __repr__(self):
        return f"{type(self).__name__}({self.as_string})"

    def __str__(self):
        return self.as_string

    @property
    def as_string(self):
        uri_parts = [f"{k}:{v}" for k, v in self._as_dict.items() if v is not None]
        return "+".join(uri_parts)

    @property
    def product_string(self) -> Optional[str]:
        candidates = [x for x in self._as_dict.items() if str(x[1]) == "1"]
        if candidates:
            return candidates[0][0]

        return None

    @property
    def channel(self) -> RobloxReleaseChannel:
        channel_str = self._as_dict.get("channel", "")
        if channel_str:
            return RobloxReleaseChannel(channel_str)

        else:
            return MAIN_ROBLOX_RELEASE_CHANNEL

    @channel.setter
    def channel(self, v: RobloxReleaseChannel):
        self._as_dict["channel"] = v.value
