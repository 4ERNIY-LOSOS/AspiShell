from gi.repository import Gtk

class RightPanel(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_css_classes(['side-panel'])
        self.set_size_request(300, -1)

        label = Gtk.Label(label="Это правая панель")
        label.set_vexpand(True)
        self.append(label)
