#!/usr/bin/env python3
"""
Скрипт для запуска тестов производительности Med-Tox backend
Запускать из корневой директории проекта
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем тесты
if __name__ == "__main__":
    import pytest
    
    # Запускаем тесты производительности
    test_file = os.path.join("test", "test_performance.py")
    exit_code = pytest.main([test_file, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n✅ Все тесты производительности прошли успешно!")
    else:
        print(f"\n❌ Тесты завершились с кодом: {exit_code}")
    
    sys.exit(exit_code)
