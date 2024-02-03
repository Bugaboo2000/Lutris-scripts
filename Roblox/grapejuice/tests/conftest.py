import uuid

import pytest

from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.wine.wineprefix import Wineprefix


@pytest.fixture
def a_launch_uri():
    return "roblox-player:1+launchmode:play+gameinfo:xyz+launchtime:111+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D111%26placeId%3D111%26isPlayTogetherGame%3Dfalse%26joinAttemptId%3Dxyz%3DPlayButton+browsertrackerid:111+robloxLocale:en_us+gameLocale:en_us+channel:"


@pytest.fixture
def a_launch_uri_no_channel():
    return "roblox-player:1+launchmode:play+gameinfo:TEST_GAME_INFO+launchtime:1692294086755+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%23452345345%26placeId%45454545%26isPlayTogetherGame%3Dfalse%26joinAttemptId%ASOIDJASDOIJAIOSJD%26joinAttemptOrigin%3DPlayButton+browsertrackerid:123123123123+robloxLocale:en_us+gameLocale:en_us"


@pytest.fixture
def a_launch_uri_no_value():
    return "roblox-player:1+launchmode:play+gameinfo:TEST_GAME_INFO+launchtime:1692294086755+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%23452345345%26placeId%45454545%26isPlayTogetherGame%3Dfalse%26joinAttemptId%ASOIDJASDOIJAIOSJD%26joinAttemptOrigin%3DPlayButton+browsertrackerid:+robloxLocale:en_us+gameLocale:en_us"


@pytest.fixture
def an_edit_cloud_game_uri():
    return "roblox-studio:1+launchmode:edit+launchtime:111+avatar+browsertrackerid:111+robloxLocale:en-US+gameLocale:en-US+channel:+browser:firefox+userId:111+distributorType:Global"


@pytest.fixture
def random_wineprefix() -> Wineprefix:
    prefix_id = str(uuid.uuid4())
    priority = 999
    name_on_disk = prefix_id
    display_name = f"Test prefix {prefix_id}"
    wine_home = ""
    dll_overrides = ""

    return Wineprefix(
        WineprefixConfigurationModel(
            id=prefix_id,
            priority=priority,
            name_on_disk=name_on_disk,
            display_name=display_name,
            wine_home=wine_home,
            dll_overrides=dll_overrides
        )
    )
