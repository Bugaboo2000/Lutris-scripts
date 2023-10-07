import logging

from grapejuice_common.models.settings_model import SettingsModel


def run_first_time_setup():
    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.errors import WineprefixNotFoundUsingHints
    from grapejuice_common.wine.wineprefix import Wineprefix
    from grapejuice_common.wine.wine_functions import \
        get_player_wineprefix, \
        get_studio_wineprefix, \
        create_player_prefix_model, \
        create_studio_prefix_model

    log = logging.getLogger("first_time_setup")

    log.info("Retrieving settings as dict")
    settings_dict = current_settings.as_dict()

    log.info("Getting player Wineprefix")
    try:
        player_prefix = get_player_wineprefix()

    except WineprefixNotFoundUsingHints:
        log.info("Creating player Wineprefix")

        player_prefix_model = create_player_prefix_model(settings_dict)

        log.info("Saving player wineprefix to settings")
        current_settings.save_prefix_model(player_prefix_model)
        settings_dict = current_settings.as_dict()

        player_prefix = Wineprefix(player_prefix_model)

    if not player_prefix:
        log.error("Player Wineprefix was not created?!")

    log.info("Getting studio Wineprefix")
    try:
        studio_prefix = get_studio_wineprefix()

    except WineprefixNotFoundUsingHints:
        log.info("Creating studio wineprefix")
        studio_prefix_model = create_studio_prefix_model(settings_dict)

        log.info("Saving studio Wineprefix to settings")
        current_settings.save_prefix_model(studio_prefix_model)

        studio_prefix = Wineprefix(studio_prefix_model)

    if not studio_prefix:
        log.error("Studio Wineprefix was not created?!")

    log.info("Completed first time setup!")

    def set_first_time_setup_in_settings(settings: SettingsModel):
        settings.performed_first_time_setup = True

    if studio_prefix and player_prefix:
        current_settings.update_model(set_first_time_setup_in_settings)
