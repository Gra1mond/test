#!/usr/bin/env python
"""Скрипт-обертка для запуска alembic миграций"""
import sys
from alembic.config import main

if __name__ == "__main__":
    sys.exit(main())
