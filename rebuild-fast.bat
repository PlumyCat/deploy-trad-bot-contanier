@echo off
REM ============================================
REM Rebuild avec Fork Aux-petits-Oignons
REM ============================================
echo.
echo ========================================
echo   BUILD - Fork Aux-petits-Oignons
echo ========================================
echo.
echo Version personnalisee avec:
echo   - 3 modeles Azure pre-configures
echo   - Welcome page Aux petits Oignons
echo   - Config entreprise verrouillee
echo.

REM Activer BuildKit
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1

echo Arret du container...
docker-compose down 2>nul

echo Suppression de l'image existante...
docker rmi auxpetitsoignons-trad-bot:latest 2>nul

echo.
echo Build avec Dockerfile...
echo Debut: %TIME%
echo.

docker build -t auxpetitsoignons-trad-bot:latest .

docker images -q auxpetitsoignons-trad-bot:latest > nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Fin: %TIME%
    echo.
    echo ========================================
    echo   BUILD REUSSI - FORK CUSTOM
    echo ========================================
    echo.
    docker images auxpetitsoignons-trad-bot
    echo.
    echo Configuration pre-configuree dans conf_opencode/.env
    echo.
    echo Pour demarrer: start.bat
    echo.
) else (
    echo.
    echo ERREUR lors du build
    echo.
)

pause
