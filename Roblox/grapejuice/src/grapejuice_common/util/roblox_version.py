from typing import Optional

import requests

from grapejuice_common.roblox_product import RobloxReleaseChannel, MAIN_ROBLOX_RELEASE_CHANNEL
from grapejuice_common.util.cache_utils import cache


# TODO: Handle fetch failures properly

@cache()
def current_player_version(
    release_channel: Optional[RobloxReleaseChannel] = MAIN_ROBLOX_RELEASE_CHANNEL
) -> Optional[str]:
    url = f"https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer/channel/{release_channel.value}"
    response = requests.get(url)
    response.raise_for_status()

    # if not response.ok:
    #     return None

    return response.json()["clientVersionUpload"]


@cache()
def current_studio_version(
    release_channel: Optional[RobloxReleaseChannel] = MAIN_ROBLOX_RELEASE_CHANNEL
) -> Optional[str]:
    url = f"https://clientsettingscdn.roblox.com/v2/client-version/WindowsStudio/channel/{release_channel.value}"
    response = requests.get(url)
    response.raise_for_status()

    # if not response.ok:
    #     return None

    return response.json()["clientVersionUpload"]
