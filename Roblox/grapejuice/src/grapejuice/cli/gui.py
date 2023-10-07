import click

from grapejuice.cli.cli_common import common_run_configuration
from grapejuice_common.gtk.gtk_util import gtk_boot


@click.command()
@common_run_configuration
def main():
    def make_main_window():
        from grapejuice.windows.main_window import MainWindow
        window = MainWindow()
        window.show()

    gtk_boot(make_main_window)


def easy_install_main():
    main()


def module_invocation_main():
    main()


if __name__ == "__main__":
    main()
