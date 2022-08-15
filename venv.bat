@echo off

RMDIR /S /Q venv

echo. creating virtual environment ...
python -m venv venv

echo. activating virtual environment ...
call venv\scripts\activate.bat

echo. upgrading pip if needed ...
python -m pip install --upgrade pip

echo. installing dependencies ...
pip install -r requirements.txt

echo.
echo. finished setting up virtual environment.
pause