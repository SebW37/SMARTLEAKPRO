@echo off
echo Starting SmartLeakPro Backend...
cd backend
call ..\venv\Scripts\activate.bat
python run.py
pause
