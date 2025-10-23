import asyncio
import json
import os
import socket
import subprocess
import threading
import logging
from gi.repository import GObject, GLib

logger = logging.getLogger(__name__)

class HyprlandIPC(GObject.Object):
    __gsignals__ = {
        'state-changed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.workspaces = []
                    cls._instance.active_workspace_id = -1
                    cls._instance.active_layout = "N/A"
                    cls._instance.is_listening = False
        return cls._instance

    def start_listener(self):
        if self.is_listening: return
        self.is_listening = True
        listener_thread = threading.Thread(target=self._run_async_main, daemon=True)
        listener_thread.start()

    def _run_async_main(self):
        asyncio.run(self._main_loop())

    async def _main_loop(self):
        await self._update_state_from_sockets()
        await self._event_listener()

    async def _event_listener(self):
        path = self._get_socket_path('.socket2.sock')
        while self.is_listening:
            try:
                reader, _ = await asyncio.open_unix_connection(path)
                while True:
                    line = await reader.readline()
                    if not line: break
                    event_type = line.decode().split('>>')[0]
                    if event_type in ('workspace', 'workspacev2', 'createworkspace', 'destroyworkspace', 'focusedmon', 'activelayout'):
                        await self._update_state_from_sockets()
            except Exception as e:
                logger.warning("Hyprland listener disconnected: %s. Reconnecting in 5s...", e)
                await asyncio.sleep(5)

    async def _update_state_from_sockets(self):
        try:
            workspaces_json = await self._query_socket('-j/workspaces')
            active_ws_json = await self._query_socket('-j/activeworkspace')
            devices_json = await self._query_socket('-j/devices')

            self.workspaces = json.loads(workspaces_json)
            self.active_workspace_id = json.loads(active_ws_json)['id']
            
            devices = json.loads(devices_json)
            main_keyboard = next((kbd for kbd in devices.get('keyboards', []) if kbd.get('main', False)), None)
            
            if main_keyboard:
                layout_name = main_keyboard.get('active_keymap', 'N/A')
                self.active_layout = layout_name[:2].upper()
            else:
                self.active_layout = "??"

            GLib.idle_add(self.emit, 'state-changed')
        except Exception as e:
            logger.error("Failed to update state from sockets", exc_info=True)

    async def _query_socket(self, command: str) -> str:
        path = self._get_socket_path('.socket.sock')
        reader, writer = await asyncio.open_unix_connection(path)
        writer.write(command.encode())
        await writer.drain()
        response = await reader.read()
        writer.close()
        await writer.wait_closed()
        return response.decode()

    @staticmethod
    def _get_socket_path(suffix: str) -> str:
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
        if not runtime_dir: raise RuntimeError("XDG_RUNTIME_DIR not set!")
        signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        if not signature: raise RuntimeError("HYPRLAND_INSTANCE_SIGNATURE not set!")
        return f"{runtime_dir}/hypr/{signature}/{suffix}"

    @staticmethod
    def dispatch(command: str, arg: str):
        try:
            subprocess.run(['hyprctl', 'dispatch', command, arg], check=True, capture_output=True)
        except Exception as e:
            logger.error("Failed to dispatch hyprctl command", exc_info=True)

ipc_client = HyprlandIPC()