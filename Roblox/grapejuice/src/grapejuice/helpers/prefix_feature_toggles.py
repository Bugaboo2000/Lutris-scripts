import logging
from dataclasses import dataclass
from gettext import gettext as _
from typing import Optional

from grapejuice import gui_task_manager
from grapejuice.tasks import InstallMicrosoftEdgeWebview2
from grapejuice_common.gtk.components.grape_setting import GrapeSetting
from grapejuice_common.gtk.components.grape_setting_action import GrapeSettingAction
from grapejuice_common.gtk.components.grape_settings_group import GrapeSettingsGroup
from grapejuice_common.gtk.components.grape_settings_pane import GrapeSettingsPane
from grapejuice_common.hardware_info.xrandr import XRandRProvider
from grapejuice_common.hardware_info.xrandr_factory import xrandr_factory
from grapejuice_common.models.wineprefix_configuration_model import ThirdPartyKeys
from grapejuice_common.roblox_product import RobloxProduct, RobloxReleaseChannel
from grapejuice_common.roblox_renderer import RobloxRenderer
from grapejuice_common.util.enum_utils import enum_value_constrained_string
from grapejuice_common.util.event import Event, Subscription
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint

log = logging.getLogger(__name__)


def _app_hints(prefix: Wineprefix) -> GrapeSettingsGroup:
    product_map = {
        RobloxProduct.app: {
            "display_name": _("Desktop App"),
            "hint": WineprefixHint.app
        },
        RobloxProduct.studio: {
            "display_name": _("Studio"),
            "hint": WineprefixHint.studio
        },
        RobloxProduct.player: {
            "display_name": _("Experience Player"),
            "hint": WineprefixHint.player
        }
    }

    def map_product(product: RobloxProduct):
        info = product_map[product]

        return GrapeSetting(
            key=enum_value_constrained_string(info["hint"]),
            display_name=info["display_name"],
            value=info["hint"].value in prefix.configuration.hints
        )

    return GrapeSettingsGroup(
        title=_("Application Hints"),
        description=_("Grapejuice uses application hints to determine which prefix should be used to launch a Roblox "
                      "application. If you toggle the hint for a Roblox application on for this prefix, Grapejuice "
                      "will use this prefix for that application."),
        settings=list(map(map_product, iter(RobloxProduct)))
    )


def _roblox_settings(prefix: Wineprefix) -> GrapeSettingsGroup:
    return GrapeSettingsGroup(
        title=_("Roblox Settings"),
        description=_("Roblox has some 'secret' launch options. You can change those here. Be careful!"),
        settings=[
            GrapeSetting(
                key="roblox_release_channel",
                display_name=_("Roblox release channel"),
                value=RobloxReleaseChannel(prefix.configuration.roblox_release_channel),
                value_type=RobloxReleaseChannel
            )
        ]
    )


def _graphics_settings(prefix: Wineprefix) -> Optional[GrapeSettingsGroup]:
    from grapejuice_common.features.settings import current_settings

    def _get_renderer():
        return RobloxRenderer(prefix.configuration.roblox_renderer)

    def _renderer_setting():
        return GrapeSetting(
            key="roblox_renderer",
            display_name=_("Roblox Renderer"),
            value_type=RobloxRenderer,
            value=_get_renderer()
        )

    def _fps_settings():
        return [
            GrapeSetting(
                key="roblox_set_target_fps",
                display_name=_("Set target FPS"),
                value=prefix.configuration.roblox_set_target_fps
            ),
            GrapeSetting(
                key="roblox_scheduler_target_fps",
                display_name=_("Target FPS"),
                value=prefix.configuration.roblox_scheduler_target_fps
            ),
        ]

    def _prime_offload_sink():
        try:
            xrandr = xrandr_factory()
            profile = current_settings.hardware_profile
            provider_index = profile.provider_index

        except Exception as e:
            log.error(str(e))
            return []

        def provider_to_string(provider: XRandRProvider):
            return f"{provider.index}: {provider.name}"

        provider_list = list(map(provider_to_string, xrandr.providers))

        return [
            GrapeSetting(
                key="should_prime",
                display_name=_("Use PRIME offloading"),
                value=prefix.configuration.prime_offload_sink > -1
            ),
            GrapeSetting(
                key="prime_offload_sink",
                display_name=_("PRIME offload sink"),
                value_type=provider_list,
                value=provider_list,
                __list_index__=provider_index
            )
        ]



    def _feral_gamemode():
        return GrapeSetting(
            key="use_feral_gamemode",
            display_name=_("Use Feral Gamemode"),
            value=prefix.configuration.use_feral_gamemode
        )

    def _enable_esync():
        return GrapeSetting(
            key="use_enable_esync",
            display_name=_("Enable Esync"),
            value=prefix.configuration.use_enable_esync

        )

    def _enable_fsync():
        return GrapeSetting(
            key="use_enable_fsync",
            display_name=_("Enable Fsync"),
            value=prefix.configuration.use_enable_fsync

        )

    def _mesa_gl_override():
        return GrapeSetting(
            key="use_mesa_gl_override",
            display_name=_("Use Mesa OpenGL version override"),
            value=prefix.configuration.use_mesa_gl_override
        )

    settings = list(filter(
        None,
        [
            _renderer_setting(),
            *_fps_settings(),
            _feral_gamemode(),
            _enable_esync(),
            _enable_fsync(),
            _mesa_gl_override(),
            *_prime_offload_sink()
        ]
    ))

    if not settings:
        return None

    return GrapeSettingsGroup(
        title=_("Graphics Settings"),
        description=_("Grapejuice can assist with graphics performance in Roblox. These are the settings that control "
                      "Grapejuice's graphics acceleration features."),
        settings=settings
    )


def _wine_debug_settings(prefix: Wineprefix):
    return GrapeSettingsGroup(
        title=_("Wine debugging settings"),
        description=_("Wine has an array of debugging options that can be used to improve wine. Some of them can cause "
                      "issues, be careful!"),
        settings=[
            GrapeSetting(
                key="enable_winedebug",
                display_name=_("Enable Wine debugging"),
                value=prefix.configuration.enable_winedebug,
            ),
            GrapeSetting(
                key="winedebug_string",
                display_name=_("WINEDEBUG string"),
                value=prefix.configuration.winedebug_string
            )
        ]
    )


def _third_party(prefix: Wineprefix):
    def do_install_edge_webview(*_):
        gui_task_manager.run_task_once(InstallMicrosoftEdgeWebview2, prefix)

    return GrapeSettingsGroup(
        title=_("Third party application integrations"),
        description=_("Grapejuice can assist in installing third party tools that will improve the Roblox experience"),
        settings=[
            GrapeSetting(
                key=ThirdPartyKeys.dxvk,
                display_name=_("Use DXVK D3D implementation"),
                value=prefix.configuration.third_party.get(ThirdPartyKeys.dxvk, False)
            ),
            GrapeSetting(
                key="install-ms-edge-webview2",
                display_name=_("Install MS Edge Webview2"),
                description=_("Clicking this option installs the Microsoft Edge Webview2 Windows component. This is "
                            "required to run Studio. The installer is broken on Wine, so you will have to kill it "
                            "manually."),
                value=GrapeSettingAction(
                    key="install-ms-edge-webview2",
                    display_name=_("Install MS Edge Webview2"),
                    action=do_install_edge_webview
                ),
            )
        ]
    )


@dataclass
class ToggleSettings:
    pass


@dataclass(frozen=True)
class Groups:
    """
    SUPER DUPER IMPORTANT COMMENT:
    IF YOU CHANGE THE ORDER OF THE SETTINGS PANEL YOU SHOULD RE-ORDER ALL OF THE ITEMS
    IN THIS DATACLASS AS WELL
    """
    winedebug: GrapeSettingsGroup
    graphics_settings: GrapeSettingsGroup
    roblox_settings: GrapeSettingsGroup
    third_party: GrapeSettingsGroup
    app_hints: GrapeSettingsGroup

    @property
    def as_list(self):
        return list(filter(
            None,
            [
                self.winedebug,
                self.graphics_settings,
                self.roblox_settings,
                self.third_party,
                self.app_hints
            ]
        ))


class PrefixFeatureToggles:
    _target_widget = None
    _current_pane: Optional[GrapeSettingsPane] = None
    _groups: Optional[Groups] = None
    _prefix: Optional[Wineprefix] = None

    _pane_changed_subscription: Optional[Subscription] = None
    changed: Event

    def __init__(self, target_widget):
        self._target_widget = target_widget
        self.changed = Event()

    def _destroy_pane(self):
        if self._pane_changed_subscription:
            self._pane_changed_subscription.unsubscribe()
            self._pane_changed_subscription = None

        if self._current_pane:
            self._target_widget.remove(self._current_pane)
            self._current_pane.destroy()
            self._current_pane = None
            self._groups = None

    def clear_toggles(self):
        self._destroy_pane()

    def use_prefix(self, prefix: Wineprefix):
        self.clear_toggles()

        self._prefix = prefix
        self._groups = Groups(*list(
            map(
                lambda c: c(prefix),
                filter(
                    None,
                    [
                        _wine_debug_settings,
                        _graphics_settings,
                        _roblox_settings,
                        _third_party,
                        _app_hints
                    ]
                )
            )
        ))

        pane = GrapeSettingsPane(groups=self._groups.as_list, min_content_height=200)

        self._target_widget.add(pane)
        pane.show_all()

        self._current_pane = pane

        self._pane_changed_subscription = Subscription(pane.changed, lambda: self.changed())

    def destroy(self):
        self._destroy_pane()

    @property
    def configured_model(self):
        model = self._prefix.configuration.copy(deep=True)
        product_hints = list(map(lambda h: h.value, [WineprefixHint.player, WineprefixHint.app, WineprefixHint.studio]))

        hints = model.hints
        hints = list(filter(lambda h: h not in product_hints, hints))
        for k, v in self._groups.app_hints.settings_dictionary.items():
            if v:
                hints.append(k)

        model.hints = hints

        model.apply_dict(self._groups.winedebug.settings_dictionary)
        model.apply_dict(self._groups.roblox_settings.settings_dictionary)

        graphics = self._groups.graphics_settings.settings_dictionary
        model.roblox_renderer = graphics.pop("roblox_renderer", RobloxRenderer.Undetermined).value
        graphics.pop("roblox_renderer", None)

        model.roblox_set_target_fps = graphics.pop("roblox_set_target_fps", False)
        model.roblox_scheduler_target_fps = graphics.pop("roblox_scheduler_target_fps", 144)

        should_prime = graphics.pop("should_prime", False)
        if should_prime and (graphics.get("prime_offload_sink", None) is not None):
            model.prime_offload_sink = int(graphics["prime_offload_sink"].split(":")[0])

        else:
            model.prime_offload_sink = -1

        graphics.pop("prime_offload_sink", None)

        model.apply_dict(graphics)

        model.third_party = self._groups.third_party.settings_dictionary
        model.third_party.pop("install-ms-edge-webview2", None)

        return model

    def __del__(self):
        self.destroy()
