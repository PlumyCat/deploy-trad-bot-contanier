@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🧅 Aux Petits Oignons
echo ========================================
echo.

set "CONFIG_FILE=%~dp0conf_opencode\.env"

:: Vérifier si la configuration existe
if not exist "%CONFIG_FILE%" (
    echo Configuration non trouvee. Lancement de la configuration...
    echo.
    call "%~dp0configure.bat"
)

:: Vérifier que le fichier a bien été créé
if not exist "%CONFIG_FILE%" (
    echo.
    echo Erreur: Configuration requise pour continuer.
    pause
    exit /b 1
)

echo Demarrage du container...
docker-compose up -d

echo.
echo Ouverture de la documentation...
start http://localhost:5545/procedure

echo.
echo Lancement d'OpenCode...
echo.
docker exec -it trad-bot-opencode opencode
