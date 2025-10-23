import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

import asyncio
import threading
import logging

from .top_bar import TopBar
from .widgets.left_panel import LeftPanel
from .widgets.right_panel import RightPanel
from .widgets.volume import VolumePopup
from ..services.audio import audio_listener

from gi.repository import Gtk4LayerShell
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method

logger = logging.getLogger(__name__)

class ShellDbusService(ServiceInterface):
    def __init__(self, shell_instance):
        super().__init__('com.aspi.shell.Control')
        self.shell = shell_instance

    @method()
    def ToggleLeftPanel(self):
        logger.info("Received ToggleLeftPanel command via DBus")
        GLib.idle_add(self.shell.on_toggle_left_panel, None)

    @method()
    def ToggleRightPanel(self):
        logger.info("Received ToggleRightPanel command via DBus")
        GLib.idle_add(self.shell.on_toggle_right_panel, None)

class Shell:
    def __init__(self, app):
        self.app = app
        self.dbus_loop = None

        # --- Верхняя панель ---
        self.top_bar = TopBar(application=app)
        self.top_bar.connect('toggle-left-panel', self.on_toggle_left_panel)
        self.top_bar.connect('toggle-right-panel', self.on_toggle_right_panel)

        # --- Левая панель-оверлей ---
        self.left_panel_window = Gtk.ApplicationWindow(application=app)
        self.left_panel_window.set_title('aspi-left-panel')
        self.left_panel_window.set_css_classes(['side-panel-window'])
        
        Gtk4LayerShell.init_for_window(self.left_panel_window)
        Gtk4LayerShell.set_namespace(self.left_panel_window, 'aspi-left-panel')
        Gtk4LayerShell.set_layer(self.left_panel_window, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self.left_panel_window, Gtk4LayerShell.Edge.LEFT, True)
        Gtk4LayerShell.set_anchor(self.left_panel_window, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self.left_panel_window, Gtk4LayerShell.Edge.BOTTOM, True)

        left_panel_content = LeftPanel()
        self.left_panel_window.set_child(left_panel_content)

        # --- Правая панель-оверлей ---
        self.right_panel_window = Gtk.ApplicationWindow(application=app)
        self.right_panel_window.set_title('aspi-right-panel')
        self.right_panel_window.set_css_classes(['side-panel-window'])
        
        Gtk4LayerShell.init_for_window(self.right_panel_window)
        Gtk4LayerShell.set_namespace(self.right_panel_window, 'aspi-right-panel')
        Gtk4LayerShell.set_layer(self.right_panel_window, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self.right_panel_window, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_anchor(self.right_panel_window, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self.right_panel_window, Gtk4LayerShell.Edge.BOTTOM, True)

        right_panel_content = RightPanel()
        self.right_panel_window.set_child(right_panel_content)

        # --- Виджет громкости (управляется слушателем звука) ---
        self.volume_popup = VolumePopup()
        audio_listener.connect('volume-changed', self.on_volume_changed)
        audio_listener.start()

    def start_dbus_service(self):
        if self.dbus_loop:
            return
        threading.Thread(target=self._run_dbus_loop, daemon=True).start()

    def _run_dbus_loop(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.dbus_loop = asyncio.get_event_loop()
        self.dbus_loop.run_until_complete(self._dbus_main())

    async def _dbus_main(self):
        try:
            bus = await MessageBus().connect()
            service_interface = ShellDbusService(self)
            bus.export('/com/aspi/shell', service_interface)
            await bus.request_name('com.aspi.shell.Control')
            logger.info("DBus service 'com.aspi.shell.Control' is running.")
            # Keep the loop running
            await bus.wait_for_disconnect()
        except Exception as e:
            logger.error("Failed to start DBus service", exc_info=True)

    def on_toggle_left_panel(self, _):
        is_visible = self.left_panel_window.is_visible()
        if is_visible:
            self.left_panel_window.hide()
        else:
            self.left_panel_window.show()

    def on_toggle_right_panel(self, _):
        is_visible = self.right_panel_window.is_visible()
        if is_visible:
            self.right_panel_window.hide()
        else:
            self.right_panel_window.show()

    def on_volume_changed(self, _, volume, is_muted):
        self.volume_popup.update_and_show(volume, is_muted)

    def present(self):
        self.top_bar.present()
        # Боковые панели и попап громкости при старте не показываем

class AspiShellApp(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.aspi.shell", **kwargs)
        self.shell = None

    def do_activate(self):
        provider = Gtk.CssProvider()
        provider.load_from_path('aspi_shell/ui/style.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        if not self.shell:
            self.shell = Shell(self)
        
        self.shell.present()
        self.shell.start_dbus_service()