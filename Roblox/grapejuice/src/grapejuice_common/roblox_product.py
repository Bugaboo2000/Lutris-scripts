from enum import Enum

_priority_mapping = {
    "roblox_player": 0,
    "roblox_studio": 1,
    "roblox_app": 2
}


class RobloxProduct(Enum):
    studio = "roblox_studio"
    player = "roblox_player"
    app = "roblox_app"

    def __lt__(self, other):
        return _priority_mapping[self.value] < _priority_mapping[other.value]


class RobloxReleaseChannel(Enum):
    LIVE = "live"
    ZLive = "zlive"
    Flag = "zflag"
    Next = "znext"
    Canary = "zcanary"
    Integration = "zintegration"
    AvatarTeam = "zavatarteam"
    SocialTeam = "zsocialteam"


MAIN_ROBLOX_RELEASE_CHANNEL = RobloxReleaseChannel.LIVE
