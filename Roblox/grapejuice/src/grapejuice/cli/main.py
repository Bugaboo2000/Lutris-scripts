import locale
import re
from gettext import gettext as _

import click

import grapejuice_common.util
from grapejuice.cli.cli_common import handle_fatal_error, common_prepare, common_exit, common_run_configuration
from grapejuice_common.gtk.gtk_util import gtk_boot


@click.group()
def cli():
    ...


@cli.command()
@click.argument("uri", type=str)
@common_run_configuration
def player(uri: str):
    def player_main():
        from grapejuice_common.abstraction.abstracted_instance import abstract_grapejuice
        from grapejuice_common.wine.wine_functions import get_player_wineprefix

        prefix = get_player_wineprefix()

        abstract_grapejuice().play_game(
            prefix.configuration.id,
            grapejuice_common.util.prepare_uri(uri)
        )

    # gtk_main is required to run the warning dialog
    gtk_boot(player_main, gtk_main=False)

    return 0


@cli.command()
@common_run_configuration
def app():
    def player_main():
        from grapejuice_common.abstraction.abstracted_instance import abstract_grapejuice
        from grapejuice_common.wine.wine_functions import get_app_wineprefix

        prefix = get_app_wineprefix()

        abstract_grapejuice().launch_app(prefix.configuration.id)

    gtk_boot(player_main, gtk_main=False)

    return 0


@cli.command()
@click.argument("uri", nargs=-1)
@common_run_configuration
def studio(uri: str):
    from grapejuice_common.wine.wine_functions import get_studio_wineprefix
    from grapejuice_common.abstraction.abstracted_instance import abstract_grapejuice

    prefix = get_studio_wineprefix()
    uri = grapejuice_common.util.prepare_uri(next(iter(uri), None))

    if uri:
        is_local = False
        if not uri.startswith("roblox-studio:"):
            uri = "Z:" + uri.replace("/", "\\")
            is_local = True

        if is_local:
            abstract_grapejuice().edit_local_game(prefix.configuration.id, uri)

        else:
            abstract_grapejuice().edit_cloud_game(prefix.configuration.id, uri)

    else:
        abstract_grapejuice().launch_studio(prefix.configuration.id)


@cli.command()
@click.argument("uri")
@common_run_configuration
def studio_auth(uri: str):
    from grapejuice_common.wine.wine_functions import get_studio_wineprefix
    from grapejuice_common.abstraction.abstracted_instance import abstract_grapejuice

    prefix = get_studio_wineprefix()
    uri = grapejuice_common.util.prepare_uri(uri)

    abstract_grapejuice().authenticate_studio(prefix.configuration.id, uri)


@cli.command()
def first_time_setup():
    from grapejuice.first_time_setup import run_first_time_setup

    run_first_time_setup()


@cli.command()
def uninstall():
    from grapejuice_common import uninstall as uninstall_module

    yes_ptn = re.compile(locale.nl_langinfo(locale.YESEXPR))
    no_ptn = re.compile(locale.nl_langinfo(locale.NOEXPR))

    uninstall_grapejuice_response = input(_("Are you sure you want to uninstall Grapejuice? [y/N] ")).strip()
    uninstall_grapejuice = yes_ptn.match(uninstall_grapejuice_response) is not None  # Check if user said yes

    if uninstall_grapejuice:
        delete_prefix_response = input(_(
            "Remove the Wineprefixes that contain your installations of Roblox? "
            "This will cause all configurations for Roblox to be permanently deleted! [n/Y] "
        )).strip()
        delete_prefix = no_ptn.match(delete_prefix_response) is None  # Check if user didn't say no

        params = uninstall_module.UninstallationParameters(delete_prefix, for_reals=True)
        uninstall_module.go(params)

        print(_("Grapejuice has been uninstalled. Have a nice day!"))

    else:
        print(_("Uninstallation aborted"))


@cli.command()
@click.argument("hint", type=str)
def top(hint: str):
    from grapejuice_common.wine.wineprefix_hints import WineprefixHint
    from grapejuice_common.wine.wine_functions import get_wineprefix

    hint = WineprefixHint(hint)
    prefix = get_wineprefix([hint])

    for proc in prefix.core_control.process_list:
        print(repr(proc))


def main():
    common_prepare()

    try:
        cli()

    except Exception as e:
        handle_fatal_error(e)

    common_exit()


def easy_install_main():
    main()


def module_invocation_main():
    main()


if __name__ == "__main__":
    main()
