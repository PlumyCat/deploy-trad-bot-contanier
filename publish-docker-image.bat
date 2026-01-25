@echo off
REM ============================================
REM Publication de l'image sur Docker Hub
REM ============================================
echo.
echo ========================================
echo   Publication Docker Hub
echo ========================================
echo.

set DOCKER_ID=becloud
set IMAGE_NAME=aux-petits-oignons
set TAG=latest

echo Docker ID: %DOCKER_ID%
echo Image: %IMAGE_NAME%
echo Tag: %TAG%
echo.

REM Vérifier que l'utilisateur est connecté
docker info | findstr "Username" >nul 2>&1
if errorlevel 1 (
    echo Connexion a Docker Hub...
    docker login
    if errorlevel 1 (
        echo.
        echo ERREUR: Connexion echouee
        pause
        exit /b 1
    )
)

echo.
echo Etape 1/3 : Build de l'image locale...
docker build -t auxpetitsoignons-trad-bot:latest .
if errorlevel 1 (
    echo ERREUR lors du build
    pause
    exit /b 1
)

echo.
echo Etape 2/3 : Tag de l'image pour Docker Hub...
docker tag auxpetitsoignons-trad-bot:latest %DOCKER_ID%/%IMAGE_NAME%:%TAG%
if errorlevel 1 (
    echo ERREUR lors du tag
    pause
    exit /b 1
)

echo.
echo Etape 3/3 : Push vers Docker Hub (environ 5-10 min)...
docker push %DOCKER_ID%/%IMAGE_NAME%:%TAG%
if errorlevel 1 (
    echo ERREUR lors du push
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Publication reussie !
echo ========================================
echo.
echo Image disponible sur:
echo https://hub.docker.com/r/%DOCKER_ID%/%IMAGE_NAME%
echo.
echo Les utilisateurs pourront maintenant faire:
echo   docker pull %DOCKER_ID%/%IMAGE_NAME%:%TAG%
echo.
pause
