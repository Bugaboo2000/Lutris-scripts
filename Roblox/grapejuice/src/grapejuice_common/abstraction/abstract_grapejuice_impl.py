import logging
from typing import Callable

from grapejuice_common.abstraction.abstract_grapejuice import AbstractGrapejuice
from grapejuice_common.recipes.delete_edge_update_service_recipe import DeleteEdgeUpdateServiceRecipe
from grapejuice_common.recipes.restore_edge_update_service_recipe import RestoreEdgeUpdateServiceRecipe
from grapejuice_common.wine.wineprefix import Wineprefix

LOG = logging.getLogger(__name__)


def _update_edge_update_state(prefix: Wineprefix):
    """
    We need to make sure the edge update service is in the correct state before each launch
    Kind of ugly to have this all the way at the top level, but it'll have to do for nwo
    :param prefix: The prefix to update the edge update service state for
    """

    if prefix.configuration.disable_edge_update:
        recipe = DeleteEdgeUpdateServiceRecipe()

    else:
        recipe = RestoreEdgeUpdateServiceRecipe()

    if not recipe.exists_in(prefix):
        recipe.make_in(prefix)


def _with_prefix_id(prefix_id: str, cb: Callable[[Wineprefix], None]):
    """
    Run an action for a prefix, while ensuring Roblox is installed.
    This function resolves the correct Wineprefix object for a given prefix id.
    :param prefix_id: The prefix id to resolve
    :param cb: Function to be called after the prefix is found (in the correct state)
    """
    from grapejuice_common.wine.wine_functions import find_wineprefix

    prefix = find_wineprefix(prefix_id)

    def cb_wrapper(pfx: Wineprefix):
        _update_edge_update_state(pfx)
        cb(pfx)

    if prefix.roblox.is_installed:
        cb_wrapper(prefix)

    else:
        prefix.roblox.install_roblox(post_install_function=lambda: cb_wrapper(prefix))


class AbstractGrapejuiceImpl(AbstractGrapejuice):
    def launch_studio(self, prefix_id: str):
        # Roblox itself does this on Windows
        # But it might cause issues which might be cause for ide=False?
        _with_prefix_id(prefix_id, lambda prefix: prefix.roblox.run_roblox_studio(ide=True))

    def play_game(self, prefix_id: str, uri: str):
        _with_prefix_id(prefix_id, lambda prefix: prefix.roblox.run_roblox_player(uri))

    def launch_app(self, prefix_id: str):
        _with_prefix_id(prefix_id, lambda prefix: prefix.roblox.launch_app())

    def edit_local_game(self, prefix_id: str, place_path: str):
        _with_prefix_id(prefix_id, lambda prefix: prefix.roblox.run_roblox_studio(uri=place_path, ide=True))

    def edit_cloud_game(self, prefix_id: str, uri: str):
        _with_prefix_id(prefix_id, lambda prefix: prefix.roblox.run_roblox_studio(uri))

    def version(self):
        from grapejuice import __version__

        return __version__

    def extract_fast_flags(self):
        from grapejuice_common.wine.wine_functions import get_studio_wineprefix
        from grapejuice_common.recipes.roblox_studio_recipe import RobloxStudioRecipe

        prefix = get_studio_wineprefix()
        recipe = RobloxStudioRecipe()

        if not recipe.exists_in(prefix):
            recipe.make_in(prefix)

        prefix.roblox.extract_fast_flags()

    def install_roblox(self, prefix_id: str):
        from grapejuice_common.wine.wine_functions import find_wineprefix

        prefix = find_wineprefix(prefix_id)
        prefix.roblox.install_roblox(post_install_function=lambda: _update_edge_update_state(prefix))

    def authenticate_studio(self, prefix_id: str, ticket: str):
        _with_prefix_id(prefix_id, lambda prefix: prefix.roblox.authenticate_studio(ticket))
