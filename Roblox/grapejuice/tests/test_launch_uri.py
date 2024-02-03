from grapejuice_common.models.launch_uri import LaunchUri
from grapejuice_common.roblox_product import RobloxReleaseChannel


def test_parse_uri_works(a_launch_uri):
    model = LaunchUri(a_launch_uri)

    v = model.as_string

    assert v == a_launch_uri


def test_can_set_channel(a_launch_uri):
    model = LaunchUri(a_launch_uri)
    channel = RobloxReleaseChannel.Integration

    model.channel = channel
    v = model.as_string

    assert v != a_launch_uri
    assert channel.value in v


def test_can_add_uri_property(a_launch_uri_no_channel):
    model = LaunchUri(a_launch_uri_no_channel)
    channel = RobloxReleaseChannel.Integration

    model.channel = channel
    v = model.as_string

    assert v != a_launch_uri_no_channel
    assert channel.value in v
    assert "+channel" in v.lower()


def test_key_has_no_value_in_uri(a_launch_uri_no_value):
    model = LaunchUri(a_launch_uri_no_value)

    assert str(model)


def test_with_empty_launch_uri():
    model = LaunchUri("")

    assert repr(model)


def tests_parse_cloud_game_uri(an_edit_cloud_game_uri):
    model = LaunchUri(an_edit_cloud_game_uri)

    assert str(model)


def test_perfect_launch_uri_reconstruction(
    a_launch_uri,
    a_launch_uri_no_channel,
    a_launch_uri_no_value,
    an_edit_cloud_game_uri
):
    for uri in (a_launch_uri, a_launch_uri_no_channel, a_launch_uri_no_value, an_edit_cloud_game_uri):
        parsed = LaunchUri(uri)

        reconstructed = parsed.as_string

        assert uri == reconstructed
