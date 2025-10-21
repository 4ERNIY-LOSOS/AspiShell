#!/bin/bash

# Переходим в директорию проекта
cd /home/merkava/AspiShell

# Активируем виртуальное окружение
source .venv/bin/activate

# Запускаем основную оболочку с LD_PRELOAD
LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so python main.py
