@echo off
echo ========================================
echo    SmartLeakPro - Démarrage Application
echo ========================================

echo.
echo 1. Vérification de l'environnement Python...
python --version
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

echo.
echo 2. Installation des dépendances...
cd backend
pip install fastapi uvicorn pydantic python-multipart

echo.
echo 3. Démarrage du serveur backend...
echo    URL: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo    Frontend: http://localhost:8000/demo
echo.
echo    Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python working_server.py

pause
