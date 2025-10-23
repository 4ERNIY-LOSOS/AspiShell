#!/bin/bash

# Переходим в директорию проекта
cd /home/merkava/AspiShell

# Активируем виртуальное окружение
source .venv/bin/activate

# Запускаем лаунчер с LD_PRELOAD
LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so python aspi_shell/ui/launcher.py
