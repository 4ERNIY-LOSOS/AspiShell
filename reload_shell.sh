#!/bin/bash

# Убивает существующий процесс оболочки
pkill -f main.py

# Запускает оболочку заново с помощью стартового скрипта
/home/merkava/AspiShell/start_shell.sh
