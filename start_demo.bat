@echo off
echo ========================================
echo    SmartLeakPro - Démarrage Démo
echo ========================================

echo.
echo 1. Démarrage du Backend (FastAPI)...
cd backend
start "SmartLeakPro Backend" cmd /k "python -c \"import uvicorn; uvicorn.run('simple_main:app', host='0.0.0.0', port=8000, reload=True)\""

echo.
echo 2. Attente du démarrage du backend...
timeout /t 5 /nobreak > nul

echo.
echo 3. Démarrage du Frontend (React)...
cd ..\frontend
start "SmartLeakPro Frontend" cmd /k "npm start"

echo.
echo ========================================
echo    SmartLeakPro est en cours de démarrage
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Appuyez sur une touche pour fermer cette fenêtre...
pause > nul
