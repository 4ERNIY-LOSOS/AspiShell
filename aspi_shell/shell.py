import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

from .top_bar import TopBar
from .widgets.left_panel import LeftPanel
from .widgets.right_panel import RightPanel

from gi.repository import Gtk4LayerShell

class Shell:
    def __init__(self, app):
        self.app = app

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

    def present(self):
        self.top_bar.present()
        # Боковые панели при старте не показываем

class AspiShellApp(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.aspi.shell", **kwargs)
        self.shell = None

    def do_activate(self):
        provider = Gtk.CssProvider()
        provider.load_from_path('data/style.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        if not self.shell:
            self.shell = Shell(self)
        
        self.shell.present()