import requests

from grapejuice_common.recipes.recipe import Recipe
from grapejuice_common.wine.wineprefix import Wineprefix


class InstallMicrosoftEdgeWebview2Recipe(Recipe):
    def __init__(self):
        super().__init__(indicators=[lambda *_: False])

    def _make_in(self, prefix: Wineprefix):
        prefix.core_control.unblock_microsoft_edge_webview2_installation()

        download_location = prefix.paths.edge_webview_directory
        download_location.mkdir(exist_ok=True, parents=True)

        response = requests.get("https://go.microsoft.com/fwlink/p/?LinkId=2124703", allow_redirects=True)
        response.raise_for_status()

        installer_location = download_location / "EvergreenBootstrapper.exe"
        with installer_location.open("wb+") as fp:
            fp.write(response.content)

        prefix.core_control.run_exe(installer_location)
