@echo off
echo.
echo ========================================
echo   Bot Traducteur - Deployment Container
echo ========================================
echo.
echo Demarrage du container...
docker-compose up -d

echo.
echo Ouverture de la documentation...
start http://localhost:5545/procedure

echo.
echo Lancement d'OpenCode...
echo.
docker exec -it trad-bot-opencode opencode
