@echo off
echo(
echo ========================================
echo   Aux Petits Oignons (Production)
echo ========================================
echo(

set "SCRIPT_DIR=%~dp0"
set "CONFIG_FILE=%SCRIPT_DIR%conf_opencode\.env"
set "ENCRYPTED_FILE=%SCRIPT_DIR%conf_opencode\credentials.encrypted"
set "DATA_DIR=%USERPROFILE%\AuxPetitsOignons"
set "DOCKER_IMAGE=becloud/aux-petits-oignons:latest"

:: Creation des dossiers de donnees
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%DATA_DIR%\clients" mkdir "%DATA_DIR%\clients"
if not exist "%DATA_DIR%\Solution" mkdir "%DATA_DIR%\Solution"

:: Verification Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo(
    echo ========================================
    echo   ERREUR: Docker n'est pas demarre !
    echo ========================================
    echo(
    echo Veuillez demarrer Docker Desktop puis relancer ce script
    echo(
    pause
    exit /b 1
)

:: Verification image Docker Hub
echo Verification de l'image Docker Hub...
docker images %DOCKER_IMAGE% | findstr "becloud" >nul 2>&1
if errorlevel 1 (
    echo(
    echo ========================================
    echo   Telechargement de l'image
    echo ========================================
    echo(
    echo L'image sera telechargee depuis Docker Hub (environ 2-3 minutes)
    echo Taille: ~2 GB
    echo(
    
    docker pull %DOCKER_IMAGE%
    
    if errorlevel 1 (
        echo(
        echo ========================================
        echo   ERREUR lors du telechargement
        echo ========================================
        echo(
        echo Verifiez votre connexion Internet
        echo(
        pause
        exit /b 1
    )
    
    echo(
    echo ========================================
    echo   Telechargement termine
    echo ========================================
    echo(
)

echo(
echo Demarrage du container..
echo(

:: Arreter et supprimer le container existant
docker stop trad-bot-opencode >nul 2>&1
docker rm trad-bot-opencode >nul 2>&1

:: Demarrer avec docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

if errorlevel 1 (
    echo(
    echo ERREUR lors du demarrage
    pause
    exit /b 1
)

echo(
echo Attente du demarrage du container...
timeout /t 5 /nobreak >nul

:: Verifier si premier demarrage (installation Bun)
docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
if errorlevel 1 (
    echo(
    echo ========================================
    echo   PREMIER DEMARRAGE DETECTE
    echo ========================================
    echo(
    echo Installation OpenCode en cours (environ 6 minutes)
    echo(
    echo Attente de la fin de l'installation...

    :wait_build
    timeout /t 10 /nobreak >nul
    docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
    if errorlevel 1 goto :wait_build

    echo(
    echo ========================================
    echo   Installation terminee
    echo ========================================
    echo(
)

echo(
echo Ouverture de la documentation..
start http://localhost:5545/procedure

echo Ouverture d'OpenCode dans une nouvelle fenetre..
start cmd /k "docker exec -it trad-bot-opencode bash -c \"set -a; source /root/.config/opencode/.env 2>/dev/null; set +a; opencode\""

echo(
echo ========================================
echo   Container pret !
echo ========================================
echo(
echo Appuyez sur Ctrl+C pour arreter le container
echo(
pause >nul

:: Nettoyage
echo(
echo Arret du container..
docker-compose -f docker-compose.prod.yml down >nul 2>&1
echo(
pause
