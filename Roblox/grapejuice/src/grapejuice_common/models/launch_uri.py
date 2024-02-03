import logging
from dataclasses import dataclass
from typing import Optional, List

from grapejuice_common.roblox_product import RobloxReleaseChannel, MAIN_ROBLOX_RELEASE_CHANNEL

log = logging.getLogger(__name__)


@dataclass
class LaunchUriPart:
    key: str
    value: str
    endswith_colon: bool = False

    @property
    def as_string(self):
        value_is_empty = len(self.value) < 1

        if value_is_empty:
            if self.endswith_colon:
                return f"{self.key}:"

            else:
                return self.key

        return f"{self.key}:{self.value}"

    @property
    def as_tuple(self):
        return (self.key, self.value)

    def __str__(self):
        return self.as_string

    @classmethod
    def from_string(cls, part: str):
        spl = part.split(":", maxsplit=1)

        if len(spl) == 1:
            spl.append("")

        key, value = spl
        endswith_colon = part.endswith(":")

        return cls(key, value, endswith_colon)


class LaunchUri:
    _initial_uri: str
    _parts: List[LaunchUriPart]

    def __init__(self, uri: str):
        self._initial_uri = uri
        self._parts = [LaunchUriPart.from_string(x) for x in uri.split("+")]

    def __repr__(self):
        return f"{type(self).__name__}({self.as_string})"

    def __str__(self):
        return self.as_string

    def get(self, item: str):
        for part in self._parts:
            if part.key == item:
                return part

        raise KeyError(item)

    def entry_iterator(self):
        for part in self._parts:
            yield part.as_tuple

    @property
    def as_string(self):
        uri_parts = [str(x) for x in self._parts]
        return "+".join(uri_parts)

    @property
    def product_string(self) -> Optional[str]:
        candidates = [x for x in self.entry_iterator() if str(x[1]) == "1"]
        if candidates:
            return candidates[0][0]

        return None

    @property
    def channel(self) -> RobloxReleaseChannel:
        try:
            channel_part = self.get("channel")
            if channel_part.value:
                return RobloxReleaseChannel(channel_part.value)

            return MAIN_ROBLOX_RELEASE_CHANNEL

        except KeyError:
            return MAIN_ROBLOX_RELEASE_CHANNEL

    @channel.setter
    def channel(self, v: RobloxReleaseChannel):
        try:
            self.get("channel").value = v.value

        except KeyError:
            self._parts.append(LaunchUriPart("channel", v.value))
