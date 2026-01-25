@echo off
echo.
echo ========================================
echo   Aux Petits Oignons
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "CONFIG_FILE=%SCRIPT_DIR%conf_opencode\.env"
set "DATA_DIR=%USERPROFILE%\AuxPetitsOignons"

:: Verification des fichiers necessaires
if not exist "%SCRIPT_DIR%docker-compose.yml" (
    echo ERREUR: docker-compose.yml manquant
    echo Repertoire: %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%conf_opencode\.env" (
    echo ERREUR: conf_opencode\.env manquant
    echo.
    pause
    exit /b 1
)

:: Creation des dossiers
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%DATA_DIR%\clients" mkdir "%DATA_DIR%\clients"
if not exist "%DATA_DIR%\Solution" mkdir "%DATA_DIR%\Solution"

:: Verification Docker
echo Verification de Docker Desktop...
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERREUR: Docker non demarre
    echo ========================================
    echo.
    echo Docker Desktop n'est pas lance.
    echo Veuillez le demarrer puis relancer ce script.
    echo.
    pause
    exit /b 1
)

echo Docker OK
echo.

:: Verification image
echo Verification de l'image Docker...
docker images auxpetitsoignons-trad-bot:latest | findstr "auxpetitsoignons-trad-bot" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Build de l'image Docker
    echo ========================================
    echo.
    echo Duree estimee: 2-3 minutes
    echo Veuillez patienter...
    echo.

    cd "%SCRIPT_DIR%"
    set DOCKER_BUILDKIT=1
    docker build -t auxpetitsoignons-trad-bot:latest . 2>&1

    if errorlevel 1 (
        echo.
        echo ========================================
        echo   ERREUR lors du build
        echo ========================================
        echo.
        pause
        exit /b 1
    )

    echo.
    echo Build termine avec succes
    echo.
)

:: Demarrer le container
echo Demarrage du container...
docker ps -a --filter "name=trad-bot-opencode" --format "{{.Names}}" | findstr "trad-bot-opencode" >nul 2>&1
if errorlevel 1 (
    echo Creation du container...
    docker-compose up -d 2>&1
    if errorlevel 1 (
        echo.
        echo ERREUR lors de la creation du container
        pause
        exit /b 1
    )
) else (
    docker start trad-bot-opencode >nul 2>&1
    if errorlevel 1 (
        echo Container corrompu, recreation...
        docker rm trad-bot-opencode >nul 2>&1
        docker-compose up -d 2>&1
    )
)

echo Container demarre
timeout /t 3 /nobreak >nul

:: Attendre installation Bun si premier demarrage
docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Premier demarrage
    echo ========================================
    echo.
    echo Installation OpenCode en cours (~6 min)
    echo.

    :wait_build
    timeout /t 10 /nobreak >nul
    docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
    if errorlevel 1 goto :wait_build

    echo Installation terminee
    echo.
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
