import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from ..hyprland import ipc_client

class Layout(Gtk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Подключаемся к сигналу нашего IPC клиента
        ipc_client.connect('state-changed', self.on_state_changed)
        
        # Устанавливаем начальное значение
        self.update_label()

    def on_state_changed(self, _):
        # Выполняем обновление в основном потоке GTK
        GLib.idle_add(self.update_label)

    def update_label(self):
        # Просто берем готовые данные из клиента
        self.set_label(ipc_client.active_layout)
        return False # для GLib.idle_add
