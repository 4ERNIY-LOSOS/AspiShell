from gi.repository import Gtk, GLib

class Clock(Gtk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Устанавливаем начальное время и запускаем таймер
        self.update_time()
        GLib.timeout_add_seconds(15, self.update_time)

    def update_time(self):
        # Получаем локальное время и форматируем его
        now = GLib.DateTime.new_now_local()
        time_str = now.format("%H:%M")
        
        # Устанавливаем текст метки
        self.set_text(time_str)
        
        # Возвращаем True, чтобы таймер продолжал работать
        return True
