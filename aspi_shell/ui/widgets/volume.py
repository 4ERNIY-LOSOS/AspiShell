import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gtk, Gdk, Gtk4LayerShell, GLib

class VolumePopup(Gtk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title('aspi-volume-popup')
        self.set_default_size(250, 60)
        self.set_css_classes(['volume-popup'])
        self.hide_timer = None

        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.TOP)
        Gtk4LayerShell.set_namespace(self, "volume-popup")
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.BOTTOM, True)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.BOTTOM, 40)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(15)
        main_box.set_margin_end(15)
        self.set_child(main_box)

        self.icon = Gtk.Image()
        self.icon.set_pixel_size(24)
        main_box.append(self.icon)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_draw_value(False)
        self.scale.set_hexpand(True)
        self.scale.set_sensitive(False)
        main_box.append(self.scale)

        self.label = Gtk.Label()
        main_box.append(self.label)

    def update_and_show(self, volume, is_muted):
        display_volume = 0 if is_muted else volume
        icon_name = "audio-volume-muted-symbolic"
        if not is_muted:
            if volume > 66:
                icon_name = "audio-volume-high-symbolic"
            elif volume > 33:
                icon_name = "audio-volume-medium-symbolic"
            else:
                icon_name = "audio-volume-low-symbolic"
        
        self.icon.set_from_icon_name(icon_name)
        self.scale.set_value(display_volume)
        self.label.set_text(f"{display_volume}%")
        
        self.set_visible(True)

        if self.hide_timer:
            GLib.source_remove(self.hide_timer)
        self.hide_timer = GLib.timeout_add(500, self.hide_popup)

    def hide_popup(self):
        self.set_visible(False)
        self.hide_timer = None
        return GLib.SOURCE_REMOVE
