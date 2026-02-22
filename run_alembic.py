#!/usr/bin/env python
"""Скрипт-обертка для запуска alembic миграций"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from alembic.config import main
except ImportError as e:
    print(f"Error importing alembic: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    # Попробуем установить alembic
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "alembic==1.13.1"])
    from alembic.config import main

if __name__ == "__main__":
    sys.exit(main())
