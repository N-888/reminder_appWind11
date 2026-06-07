@echo off
REM Запуск приложения Напоминалка
REM Этот файл автоматически установит зависимости и запустит приложение

echo.
echo ========================================
echo    НАПОМИНАЛКА - Desktop Application
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python не установлен!
    echo Пожалуйста, установите Python 3.7+ с сайта python.org
    pause
    exit /b 1
)

echo [✓] Python найден

REM Установка зависимостей
echo.
echo [*] Проверка зависимостей...
pip install -q -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ошибка при установке зависимостей!
    echo Попытка установки с полным выводом...
    pip install -r requirements.txt
    pause
    exit /b 1
)

echo [✓] Зависимости установлены

REM Запуск приложения
echo.
echo [*] Запуск приложения...
echo.
python main.py

pause
