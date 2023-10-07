from pathlib import Path

from grapejuice_common import paths
from grapejuice_common.gtk.gtk_util import gtk_boot
from grapejuice_common.logs.log_vacuum import vacuum_logs


def handle_fatal_error(ex: Exception):
    print("Fatal error: " + str(ex))

    def make_exception_window():
        from grapejuice.windows.exception_viewer import ExceptionViewer
        window = ExceptionViewer(exception=ex, is_main=True)

        window.show()

    gtk_boot(make_exception_window)


def _load_locale() -> Path:
    import gettext
    import locale
    text_domain = "grapejuice"
    locale_directory = paths.locale_directory()

    gettext.bindtextdomain(text_domain, locale_directory)
    gettext.textdomain(text_domain)
    locale.bindtextdomain(text_domain, locale_directory)
    locale.setlocale(locale.LC_ALL, "")

    return locale_directory


def common_prepare():
    locale_directory = None
    locale_loading_errors = None

    try:
        locale_directory = _load_locale()

    except Exception as e:
        locale_loading_errors = e

    from grapejuice_common.logs import log_config

    log_config.configure_logging("grapejuice")

    # List out startup info
    # Has to be done after configure_logging to avoid load order conflicts
    import logging
    log = logging.getLogger("common_prepare")

    if locale_loading_errors is not None:
        log.error(f"Failed to configure locale: {locale_loading_errors}")

    if locale_directory is not None:
        log.info(f"Using locale directory {locale_directory}")

    from grapejuice_common.features.settings import current_settings

    if current_settings:
        if not current_settings.get_model().performed_first_time_setup:
            from grapejuice.first_time_setup import run_first_time_setup
            run_first_time_setup()

        current_settings.perform_migrations()


def common_exit():
    vacuum_logs()


def common_run_configuration(fn):
    def wrapper(*args, **kwargs):
        return_value = None

        try:
            common_prepare()
            return_value = fn(*args, **kwargs)

        except Exception as e:
            handle_fatal_error(e)

        finally:
            common_exit()

        return return_value

    setattr(wrapper, "__name__", getattr(fn, "__name__"))

    return wrapper
