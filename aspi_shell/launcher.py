import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gtk, Gdk, Gtk4LayerShell
import os
import sys
from pathlib import Path
import configparser
import subprocess
import shlex

class LauncherWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(600, 350)

        # Настройка Gtk4LayerShell
        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.EXCLUSIVE)

        # Основной контейнер
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.set_child(main_box)

        # Поле для ввода
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Поиск приложений...")
        self.search_entry.connect("changed", self.on_changed)
        main_box.append(self.search_entry)

        # Список для результатов
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        self.results_list_box = Gtk.ListBox()
        self.results_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.results_list_box.connect("row-activated", self.on_row_activated)
        scrolled_window.set_child(self.results_list_box)
        main_box.append(scrolled_window)

        # Логика закрытия
        evk = Gtk.EventControllerKey.new()
        evk.connect("key-pressed", self.on_key_pressed)
        self.add_controller(evk)

        # Находим и загружаем приложения
        self.applications = []
        self.load_applications()

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.close()
        return False

    def on_row_activated(self, listbox, row):
        self.launch_selected_app()

    def on_changed(self, entry):
        search_text = entry.get_text().lower()
        if not search_text:
            filtered_apps = self.applications
        else:
            filtered_apps = [
                app for app in self.applications 
                if search_text in app['name'].lower()
            ]
        self._populate_app_list(filtered_apps)

    def launch_selected_app(self):
        selected_row = self.results_list_box.get_selected_row()
        if not selected_row:
            # Если ничего не выбрано, запускаем первый элемент в списке
            selected_row = self.results_list_box.get_row_at_index(0)
            if not selected_row:
                return

        app_info = selected_row.app_info
        exec_command = app_info['exec']
        
        command_to_run = ' '.join([part for part in exec_command.split() if not part.startswith('%')])

        print(f"Launching: {command_to_run}")
        try:
            args = shlex.split(command_to_run)
            subprocess.Popen(args)
            self.get_application().quit()
        except Exception as e:
            print(f"Failed to launch {command_to_run}: {e}")

    def load_applications(self):
        desktop_files = self._find_desktop_files()
        for file_path in desktop_files:
            app_info = self._parse_desktop_file(file_path)
            if app_info:
                self.applications.append(app_info)
        
        self.applications.sort(key=lambda app: app['name'])
        print(f"Loaded {len(self.applications)} applications.")
        self._populate_app_list(self.applications)

    def _populate_app_list(self, apps):
        while (child := self.results_list_box.get_first_child()) is not None:
            self.results_list_box.remove(child)

        for app in apps:
            row = Gtk.ListBoxRow()
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_margin_top(5)
            hbox.set_margin_bottom(5)
            hbox.set_margin_start(5)
            hbox.set_margin_end(5)
            
            icon = Gtk.Image.new_from_icon_name(app.get('icon'))
            icon.set_pixel_size(32)
            hbox.append(icon)
            
            label = Gtk.Label.new(app.get('name'))
            label.set_xalign(0)
            hbox.append(label)
            
            row.set_child(hbox)
            row.app_info = app 
            
            self.results_list_box.append(row)

    def _find_desktop_files(self):
        desktop_files = []
        app_dirs = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            str(Path.home() / '.local/share/applications')
        ]

        for app_dir in app_dirs:
            if not os.path.isdir(app_dir):
                continue
            for root, _, files in os.walk(app_dir):
                for file in files:
                    if file.endswith('.desktop'):
                        desktop_files.append(os.path.join(root, file))
        
        return desktop_files

    def _parse_desktop_file(self, file_path):
        try:
            config = configparser.ConfigParser(interpolation=None)
            config.optionxform = str
            config.read(file_path, encoding='utf-8')

            if 'Desktop Entry' in config:
                entry = config['Desktop Entry']
                if entry.getboolean('NoDisplay', False):
                    return None
                
                if 'Name' in entry and 'Exec' in entry:
                    return {
                        'name': entry.get('Name'),
                        'exec': entry.get('Exec'),
                        'icon': entry.get('Icon', None)
                    }
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return None

class LauncherApp(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.aspi.launcher", **kwargs)
        self.window = None

    def do_activate(self):
        provider = Gtk.CssProvider()
        provider.load_from_path('data/style.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        if not self.window:
            self.window = LauncherWindow(application=self)
        self.window.present()

if __name__ == "__main__":
    app = LauncherApp()
    app.run(sys.argv)
