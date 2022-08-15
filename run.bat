@echo off

echo. checking virtual environment ...
if not exist venv\Scripts\python.exe (
    echo. virtual environment has not been set-up.
    pause
    exit /B 1
)

echo. activating virtual environment ...
call venv\scripts\activate.bat

echo. running application ...
echo.
python src/app.py %*
pause