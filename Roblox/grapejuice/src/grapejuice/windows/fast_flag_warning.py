from grapejuice_common import paths
from grapejuice_common.features.settings import current_settings
from grapejuice_common.gtk.gtk_base import GtkBase
from grapejuice_common.models.settings_model import SettingsModel


class FastFlagWarning(GtkBase):
    def __init__(self, callback):
        super().__init__(
            glade_path=paths.fast_flag_warning_glade(),
            handler_instance=self,
            root_widget_name="fast_flag_warning"
        )

        self._do_continue = False
        self._callback = callback

        self.warn_check.set_active(current_settings.get_model().show_fast_flag_warning)

    @property
    def window(self):
        return self.root_widget

    @property
    def devforum_link(self):
        return self.widgets.devforum_link

    @property
    def warn_check(self):
        return self.widgets.warn_check

    def destroy(self):
        self.window.destroy()

    def on_close(self, *_):
        if self._do_continue:
            def update_model_fn(mdl: SettingsModel):
                mdl.show_fast_flag_warning = self.warn_check.get_active()

            current_settings.update_model(update_model_fn)

        self._callback(self._do_continue)

    def abort(self, *_):
        self._do_continue = False
        self.destroy()

    def open_editor(self, *_):
        self._do_continue = True
        self.destroy()

    def show_forum_post(self, link_button):
        pass

    def show(self):
        self.window.show()
