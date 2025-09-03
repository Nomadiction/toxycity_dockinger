#!/usr/bin/env python3
"""
Простой скрипт для запуска MedTox приложения
"""

import subprocess
import sys

def main():
    print("=" * 50)
    print("💊 MedTox - Система анализа токсичности лекарств")
    print("=" * 50)
    
    print("🚀 Запуск backend сервера...")
    print("📊 Backend будет доступен на: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        # Запускаем backend
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app_backend:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
