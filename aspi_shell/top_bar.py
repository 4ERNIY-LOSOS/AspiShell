import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')

from gi.repository import Gtk, Gdk, Gtk4LayerShell, GObject
from .widgets.clock import Clock
from .widgets.workspaces import Workspaces
from .widgets.layout import Layout

class TopBar(Gtk.ApplicationWindow):
    __gsignals__ = {
        'toggle-left-panel': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'toggle-right-panel': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Возвращаем правильное поведение слоя ---
        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.TOP)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.LEFT, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_exclusive_zone(self, 40)

        self.set_default_size(1, 40)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.set_margin_start(5)
        main_box.set_margin_end(5)
        self.set_child(main_box)

        # --- Левая часть ---
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        left_box.set_halign(Gtk.Align.START)
        main_box.append(left_box)

        left_toggle_btn = Gtk.Button.new_from_icon_name('view-list-symbolic')
        left_toggle_btn.connect('clicked', lambda w: self.emit('toggle-left-panel'))
        left_box.append(left_toggle_btn)

        workspaces_widget = Workspaces()
        left_box.append(workspaces_widget)

        # --- Центральная часть ---
        center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        center_box.set_halign(Gtk.Align.CENTER)
        center_box.set_hexpand(True)
        main_box.append(center_box)

        # --- Правая часть ---
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        right_box.set_halign(Gtk.Align.END)
        main_box.append(right_box)

        layout = Layout()
        right_box.append(layout)

        clock = Clock()
        right_box.append(clock)

        right_toggle_btn = Gtk.Button.new_from_icon_name('open-menu-symbolic')
        right_toggle_btn.connect('clicked', lambda w: self.emit('toggle-right-panel'))
        right_box.append(right_toggle_btn)