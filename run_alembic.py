#!/usr/bin/env python
"""Скрипт-обертка для запуска alembic миграций"""
import sys
import os
import subprocess

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Пытаемся импортировать alembic
try:
    from alembic.config import main
except ImportError as e:
    print(f"Error importing alembic: {e}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    print(f"Current directory: {os.getcwd()}", file=sys.stderr)
    print("Attempting to install alembic...", file=sys.stderr)
    # Попробуем установить alembic
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "alembic==1.13.1"], 
                            stdout=sys.stderr, stderr=sys.stderr)
        from alembic.config import main
        print("Alembic installed successfully", file=sys.stderr)
    except Exception as install_error:
        print(f"Failed to install alembic: {install_error}", file=sys.stderr)
        # Попробуем использовать системный alembic через subprocess
        print("Trying to use system alembic...", file=sys.stderr)
        result = subprocess.run(["alembic"] + sys.argv[1:], 
                               capture_output=False)
        sys.exit(result.returncode)

if __name__ == "__main__":
    sys.exit(main())
