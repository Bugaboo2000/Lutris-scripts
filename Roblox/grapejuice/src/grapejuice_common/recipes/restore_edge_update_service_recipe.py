import logging

from grapejuice_common import paths
from grapejuice_common.recipes.recipe import Recipe
from grapejuice_common.wine.registry_file import RegistryFile
from grapejuice_common.wine.wineprefix import Wineprefix

log = logging.getLogger(__name__)


def _have_edge_update_service(prefix: Wineprefix):
    system_hive = RegistryFile(prefix.paths.system_registry_hive)
    try:
        system_hive.load()

    except FileNotFoundError as e:
        log.error("Could not load System Hive")
        log.error(f"{type(e).__name__}: {e}")

        return False

    edge_update = system_hive.find_key(r"System\\CurrentControlSet\\Services\\edgeupdate")
    edge_update_m = system_hive.find_key(r"System\\CurrentControlSet\\Services\\edgeupdatem")

    log.info(f"Edge update: {repr(edge_update)}")
    log.info(f"Edge update M: {repr(edge_update_m)}")

    have_edge_update = edge_update is not None
    have_edge_update_m = edge_update_m is not None

    return have_edge_update and have_edge_update_m


class RestoreEdgeUpdateServiceRecipe(Recipe):
    def __init__(self):
        super().__init__(indicators=[_have_edge_update_service])

    def _make_in(self, prefix: Wineprefix):
        log.info(f"Restoring edge update service in prefix {prefix.configuration.display_name}")

        edge_webview_directory = paths.assets_directory() / "edge_webview"
        edgeupdate_service_path = edge_webview_directory / "edgeupdate_service.reg"
        edgeupdatem_service_path = edge_webview_directory / "edgeupdatem_service.reg"

        prefix.core_control.load_registry_file(edgeupdate_service_path)
        prefix.core_control.load_registry_file(edgeupdatem_service_path)
