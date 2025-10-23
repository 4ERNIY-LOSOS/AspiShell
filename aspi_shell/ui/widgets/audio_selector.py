import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib
import pulsectl
import os
import re
from pathlib import Path
from ...utils.config import config_manager

def get_short_name(device):
    """Аккуратно сокращает оригинальное имя устройства."""
    desc = device.description
    # Убираем только самый явный технический мусор
    desc = re.sub(r'\s*Analog Stereo', '', desc)
    desc = re.sub(r'\s*Digital Stereo \(.*\)', '', desc)
    
    # Если имя все еще слишком длинное, обрезаем
    if len(desc) > 40:
        return desc[:37] + '...'
    
    return desc.strip() if desc.strip() else device.description # Возвращаем оригинал, если все стерли

class AudioDeviceRow(Gtk.ListBoxRow):
    def __init__(self, device_description, device_name, is_active):
        super().__init__()
        self.device_name = device_name

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.set_margin_top(8)
        main_box.set_margin_bottom(8)
        main_box.set_margin_start(8)
        main_box.set_margin_end(8)
        self.set_child(main_box)

        if is_active:
            icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
            main_box.append(icon)
        
        label = Gtk.Label.new(device_description)
        label.set_xalign(0)
        label.set_hexpand(True)
        label.set_wrap(True) # Включаем перенос текста
        label.set_wrap_mode(Gtk.WrapMode.WORD_CHAR) # Режим переноса
        main_box.append(label)

class AudioSelector(Gtk.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_icon_name("multimedia-volume-control-symbolic")
        self.connect('clicked', self.on_clicked)
        self.popover = None

    def on_clicked(self, button):
        self.popover = Gtk.Popover.new()
        self.popover.set_parent(self)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.set_child(container)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        container.append(stack_switcher)
        container.append(stack)

        with pulsectl.Pulse('aspi-audio-selector') as pulse:
            hidden_devices_str = config_manager.get('audio', 'hidden_devices', fallback='')
            hidden_devices = {name.strip() for name in hidden_devices_str.split(',') if name.strip()}
            server_info = pulse.server_info()

            # --- Страница вывода ---
            sinks = pulse.sink_list()
            output_listbox = Gtk.ListBox()
            output_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            output_listbox.add_css_class('boxed-list')
            output_listbox.connect('row-activated', self._on_sink_activated)
            output_listbox.set_vexpand(True)
            for sink in sinks:
                if 'monitor' in sink.name or any(hidden in sink.name for hidden in hidden_devices):
                    continue
                is_active = sink.name == server_info.default_sink_name
                short_name = get_short_name(sink)
                row = AudioDeviceRow(short_name, sink.name, is_active)
                output_listbox.append(row)
            
            stack.add_titled(output_listbox, "output", "Вывод")

            # --- Страница ввода ---
            sources = pulse.source_list()
            input_listbox = Gtk.ListBox()
            input_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            input_listbox.add_css_class('boxed-list')
            input_listbox.connect('row-activated', self._on_source_activated)
            input_listbox.set_vexpand(True)
            for source in sources:
                if any(hidden in source.name for hidden in hidden_devices):
                    continue
                is_active = source.name == server_info.default_source_name
                short_name = get_short_name(source)
                row = AudioDeviceRow(short_name, source.name, is_active)
                input_listbox.append(row)

            stack.add_titled(input_listbox, "input", "Ввод")

        self.popover.popup()

    def _on_sink_activated(self, listbox, row):
        sink_name = row.device_name
        with pulsectl.Pulse('aspi-audio-setter') as pulse:
            pulse.sink_default_set(sink_name)
        self.popover.popdown()

    def _on_source_activated(self, listbox, row):
        source_name = row.device_name
        with pulsectl.Pulse('aspi-audio-setter') as pulse:
            pulse.source_default_set(source_name)
        self.popover.popdown()