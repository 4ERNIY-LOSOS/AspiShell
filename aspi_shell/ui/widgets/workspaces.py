from gi.repository import Gtk, GLib
from ...core.hyprland import ipc_client

class Workspaces(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(5)

        # Подключаемся к сигналу изменения состояния
        ipc_client.connect('state-changed', self.on_state_changed)
        
        # Запускаем фоновый слушатель (он же вызовет и первую отрисовку)
        ipc_client.start_listener()

    def on_state_changed(self, _):
        # GLib.idle_add гарантирует, что отрисовка произойдет в основном потоке GTK
        GLib.idle_add(self.render_workspaces)

    def on_workspace_clicked(self, _, ws_id):
        ipc_client.dispatch('workspace', str(ws_id))

    def render_workspaces(self):
        # Очищаем старые виджеты
        child = self.get_first_child()
        while child:
            self.remove(child)
            child = self.get_first_child()

        # Просто берем готовые данные из клиента
        all_workspaces = ipc_client.workspaces
        active_ws_id = ipc_client.active_workspace_id

        # Фильтруем системные воркспейсы (с отрицательным ID)
        workspaces = [ws for ws in all_workspaces if ws['id'] > 0]

        # Сортируем по ID
        workspaces.sort(key=lambda w: w['id'])

        for ws in workspaces:
            btn = Gtk.Button(label=str(ws['id']))
            style_context = btn.get_style_context()

            if ws['id'] == active_ws_id:
                style_context.add_class('focused')
            
            btn.connect('clicked', self.on_workspace_clicked, ws['id'])
            
            self.append(btn)
        
        return False # Для GLib.idle_add
