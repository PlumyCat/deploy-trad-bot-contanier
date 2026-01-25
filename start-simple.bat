@echo off
echo.
echo ========================================
echo   Aux Petits Oignons
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "CONFIG_FILE=%SCRIPT_DIR%conf_opencode\.env"
set "DATA_DIR=%USERPROFILE%\AuxPetitsOignons"

:: Creation des dossiers
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%DATA_DIR%\clients" mkdir "%DATA_DIR%\clients"
if not exist "%DATA_DIR%\Solution" mkdir "%DATA_DIR%\Solution"

:: Verification Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Docker n'est pas demarre
    echo.
    pause
    exit /b 1
)

:: Verification image
docker images auxpetitsoignons-trad-bot:latest | findstr "auxpetitsoignons-trad-bot" >nul 2>&1
if errorlevel 1 (
    echo Build de l'image Docker (environ 2-3 min)...
    echo.
    cd "%SCRIPT_DIR%"
    set DOCKER_BUILDKIT=1
    docker build -t auxpetitsoignons-trad-bot:latest .
    if errorlevel 1 (
        echo ERREUR lors du build
        pause
        exit /b 1
    )
)

:: Demarrer le container
docker ps -a --filter "name=trad-bot-opencode" --format "{{.Names}}" | findstr "trad-bot-opencode" >nul 2>&1
if errorlevel 1 (
    echo Creation du container...
    docker-compose up -d
) else (
    echo Demarrage du container...
    docker start trad-bot-opencode >nul 2>&1
)

timeout /t 3 /nobreak >nul

:: Attendre installation Bun si premier demarrage
docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
if errorlevel 1 (
    echo.
    echo Premier demarrage : Installation OpenCode (~6 min)
    echo.
    :wait_build
    timeout /t 10 /nobreak >nul
    docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
    if errorlevel 1 goto :wait_build
)

echo.
echo ========================================
echo   Container pret
echo ========================================
echo.
echo Documentation : http://localhost:5545/procedure
echo.
echo Pour utiliser OpenCode :
echo   docker exec -it trad-bot-opencode bash
echo.
echo Puis dans le container :
echo   opencode        (nouvelle conversation)
echo   opencode -c     (reprendre conversation)
echo.
echo Pour arreter :
echo   docker stop trad-bot-opencode
echo.

start http://localhost:5545/procedure

pause
