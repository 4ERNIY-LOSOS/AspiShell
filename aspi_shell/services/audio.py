import asyncio
import threading
import pulsectl_asyncio
import logging
from gi.repository import GObject, GLib
from pulsectl import PulseEventMaskEnum

logger = logging.getLogger(__name__)

class AudioListener(GObject.Object):
    __gsignals__ = {
        'volume-changed': (GObject.SignalFlags.RUN_FIRST, None, (int, bool)) # volume_percent, is_muted
    }

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.is_listening = False
                    cls._instance._is_first_check = True # Флаг для первой проверки
                    cls._instance._last_volume = -1 # Храним последнее известное состояние
                    cls._instance._last_muted = False
        return cls._instance

    def start(self):
        if self.is_listening:
            return
        self.is_listening = True
        thread = threading.Thread(target=self._run_async_loop, daemon=True)
        thread.start()

    def _run_async_loop(self):
        asyncio.run(self._main())

    async def _main(self):
        while self.is_listening:
            try:
                async with pulsectl_asyncio.PulseAsync('aspi-shell-volume-monitor') as pulse:
                    # Получаем первоначальное состояние
                    await self._get_default_sink_info(pulse)
                    # Подписываемся на события и итерируемся по ним
                    async for event in pulse.subscribe_events(PulseEventMaskEnum.sink):
                        if event.facility == 'sink' and event.t == 'change':
                            await self._get_default_sink_info(pulse)
            except Exception as e:
                logger.warning("Audio listener error: %s. Reconnecting in 5s...", e)
                await asyncio.sleep(5)

    async def _get_default_sink_info(self, pulse):
        try:
            server_info = await pulse.server_info()
            default_sink_name = server_info.default_sink_name
            
            sinks = await pulse.sink_list()
            for sink in sinks:
                if sink.name == default_sink_name:
                    volume_percent = int(sink.volume.value_flat * 100)

                    # Если это первая проверка при запуске, не показываем виджет
                    if self._is_first_check:
                        self._is_first_check = False
                        self._last_volume = volume_percent # Сохраняем начальное состояние
                        self._last_muted = sink.mute
                        return

                    # Только если громкость или mute изменились, подаем сигнал
                    if volume_percent != self._last_volume or sink.mute != self._last_muted:
                        self._last_volume = volume_percent
                        self._last_muted = sink.mute
                        GLib.idle_add(self.emit, 'volume-changed', volume_percent, sink.mute)
                    break
        except Exception as e:
            logger.error("Error getting sink info", exc_info=True)


audio_listener = AudioListener()
